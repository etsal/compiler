from compiler.codegen.expr import irgen_lvalue as irgen_lvalue, irgen_expr as irgen_expr
from llvmlite import ir as ir


def irgen_stmt(stmt, builder, table):
    
    operator = stmt.operator
    if operator == "ret":
        if not stmt.exprs:
            return builder.ret_void()
        else:
            retval = irgen_expr(stmt.exprs[0], builder, table)
            return builder.ret(retval) 
    elif operator == "continue":
        tmp = builder.unreachable()             
        if stmt.label:
            table.conts[tmp] = (builder.block, table[stmt.label])
        else:
            table.conts[tmp] = (builder.block, None)
        return tmp
    elif operator == "break":
        tmp = builder.unreachable()             
        if stmt.label:
            table.breaks[tmp] = (builder.block, table[stmt.label])
        else:
            table.breaks[tmp] = (builder.block, None) 
        return tmp
    elif operator == "call":
        args = [irgen_expr(expr, builder, table) for expr in stmt.exprs]
        return builder.call(table.funcs[stmt.value], args)
    elif operator == "assign":
        lvalue = irgen_lvalue(stmt.exprs[0], builder, table)
        expr = irgen_expr(stmt.exprs[1], builder, table)
        return builder.store(expr, lvalue)


def irgen_block(func, block, table):
    irgen = dict({"if" : irgen_if,
                  "loop" : irgen_loop,
                  "basic" : irgen_basic,
                  "container" : irgen_container,
                })

    btype = block.type
    return irgen[btype](func, block, table)


def irgen_if(func, block, table):
    start = func.append_basic_block()
    builder = ir.IRBuilder(start)
    pred = irgen_expr(block.cond, builder, table)


    temp = builder.unreachable()
    
    if_blks = irgen_block(func, block.if_path, table)

    else_blks = []
    if block.else_path:
        else_blks += irgen_block(func, block.else_path, table)
    else:
        else_blks = [func.append_basic_block()]
        else_builder = ir.IRBuilder(else_blks[0])
        tmp = else_builder.unreachable() 
        table.nexts[tmp] = (builder.block, None)

    start.replace(temp, ir.ConditionalBranch(start, "br", [pred, if_blks[0], else_blks[0]]))
    
        

    return [start] + if_blks + else_blks 

         
def irgen_loop(func, block, table):
    blks = []

    entry = func.append_basic_block(block.label)
    

    blks = irgen_block(func, block.block, table)

    entry_builder = ir.IRBuilder(entry)
    entry_builder.branch(blks[0])

    # In case the last block is unfinished
    exit = blks[-1]
    if isinstance(exit.instructions[-1], ir.Unreachable) and \
        exit.instructions[-1] in table.nexts:
        exit.replace(exit.instructions[-1], ir.Branch(exit, "br", [entry])) 
    else:
        exit = func.append_basic_block()
        exit_builder = ir.IRBuilder(exit)
        exit_builder.branch(entry)

    for blk in blks:
        for inst in blk.instructions:
            if inst in table.breaks:
                (b, lab) = table.breaks[inst]
                if not lab or (block.label and lab == block.label):
                    table.breaks.pop(inst)
                    table.nexts[inst] = (b, lab)

            if inst in table.conts:
                (b, lab) = table.conts[inst]
                if not lab or (block.label and lab == block.label):
                    table.conts.pop(inst)
                    b.replace(inst, ir.Branch(exit, "br", [entry])) 
                    

    return [entry] + blks + [exit]

        

def irgen_container(func, block, table):
    blks = []
    children = []
    for child in block.children:
        previous = children
        children = irgen_block(func, child, table)
        for blk in previous:
            if isinstance(blk.instructions[-1], ir.Unreachable) and \
               blk.instructions[-1] in table.nexts:
                blk.replace(blk.instructions[-1], ir.Branch(blk, "br", [children[0]]))

        blks += children 

    return blks 
    

def irgen_basic(func, block, table):
    blk = func.append_basic_block()
    builder = ir.IRBuilder(blk)
    
    for stmt in block.stmts:
        irgen_stmt(stmt, builder, table)
            
    if not blk.is_terminated:
        tmp = builder.unreachable() 
        table.nexts[tmp] = (builder.block, None)

    return [blk]
        

