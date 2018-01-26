""" 
    IR Block Creation module. The goal of each of the four functions
is to produce self-contained series blocks, with the exception of 
terminators to be backpatched. 

Arguments:
func -- The IR function, used for its .append_basic_block() method
block -- The semantic block to be turned into a sequence of IR blocks
table -- A table with instructions to be backpatched

Return:
blks -- A sequence of IR blocks
"""

from compiler.codegen.expr import irgen_expr as irgen_expr, irtype as irtype
from compiler.codegen.stmt import irgen_stmt as irgen_stmt
from llvmlite import ir as ir

def mark_backpatch(builder, table):
    instr = builder.unreachable() 
    table[instr] = (builder.block, None)

def backpatch(block, instr):
    block.replace(block.terminator, instr)
    block.terminator = instr 

def irgen_block(func, block, table):
    irgen = dict({"if" : irgen_if,
                  "loop" : irgen_loop,
                  "basic" : irgen_basic,
                  "container" : irgen_container,
                })

    btype = block.type
    return irgen[btype](func, block, table)



def irgen_if(func, block, table):
    """Generate the blocks representing an if-elif*-else? statement"""
    start = func.append_basic_block()
    builder = ir.IRBuilder(start)


    pred = irgen_expr(block.cond, builder, table)
    if pred.type == ir.IntType(8):
        pred = builder.icmp_signed("!=", pred, ir.Constant(ir.IntType(8), 0))
    
    # WIll be patched with a conditional branch to the two paths
    temp = builder.unreachable()    

    # The two paths, if there is no else path 
    # we create a stub one to be optimized out by LLVM
    if_blks = irgen_block(func, block.if_path, table)
    else_blks = []
    if block.else_path:
        # Elif chains are here if they exist
        else_blks += irgen_block(func, block.else_path, table)
    else:
        else_blks = [func.append_basic_block()]
        else_builder = ir.IRBuilder(else_blks[0])
        mark_backpatch(else_builder, table.nexts)

    branch = ir.ConditionalBranch(start, "br", [pred, if_blks[0], else_blks[0]])
    start.replace(temp, branch)
    start.terminator = branch 
    return [start] + if_blks + else_blks 


         
def irgen_loop(func, block, table):
    """Generate the blocks representing a loop"""

    blks = irgen_block(func, block.block, table)
    entry = blks[0]
    exit = blks[-1]

    # In case the last block is has an instruction to be patched,
    # we patch it with a jump to the entry block
    if exit.terminator in table.nexts:
        branch = ir.Branch(exit, "br", [entry])
        backpatch(exit, branch)

    # Backpatching 
    for blk in blks:
        term= blk.terminator
        # Breaks out of the current loop are nexts 
        # to the basic block following it 
        if term in table.breaks:
            (b, lab) = table.breaks[term]
            if not lab or (block.label and lab == block.label):
                table.breaks.pop(term)
                table.nexts[term] = (b, lab)

        # Conts on the current loop can be backpatched immediately 
        if term in table.conts:
            (b, lab) = table.conts[term]
            if not lab or (block.label and lab == block.label):
                table.conts.pop(term)
                branch = ir.Branch(exit, "br", [entry])
                backpatch(b, branch)
                b.terminator = branch 

    return blks 



def irgen_basic(func, block, table):
    """Generate the blocks representing a basic block"""
    blk = func.append_basic_block()
    builder = ir.IRBuilder(blk)
    
    for stmt in block.stmts:
        irgen_stmt(stmt, builder, table)
            
    # Placeholder to be backpatched into a branch to the next instruction,
    # thus satisfying LLVM IR constraints about terminators and basic blocks
    if not blk.is_terminated:
        mark_backpatch(builder, table.nexts)

    return [blk]
   
     

def irgen_container(func, block, table):
    """Generate the blocks representing a sequence of blocks of the other types"""
    blks = []
    children = []
    for child in block.children:
        previous = children
        children = irgen_block(func, child, table)
        # Backpatch "next" undefined instructions 
        # We check all blocks, because if-else and loops can have multiple next's 
        for blk in previous:
            if blk.terminator in table.nexts:
                branch = ir.Branch(blk, "br", [children[0]])
                backpatch(blk, branch)

        blks += children 

    return blks 
    
