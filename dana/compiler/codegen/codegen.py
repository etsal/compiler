import sys
from copy import copy
from collections import deque as deque
from compiler.parser.lexer import lex as lex, tokens as tokens
from compiler.parser.parser import parser as parser
from compiler.semantic.semantic import produce_program as produce_program
from compiler.semantic.semantic import builtins as builtins
from llvmlite import ir as ir

strings = dict()
function_table = dict()
block_table = dict()
unpatched_break = dict()
unpatched_cont = dict()
unpatched_next = dict()

def irtype(dana_type, no_arrays = False):
    ir_base = dict({"int"   : ir.IntType(32),
                    "byte"  : ir.IntType(8),
                    "logic" : ir.IntType(1),
                    "void"  : ir.VoidType(),
                    "label" : ir.LabelType(),
                    })
    t = ir_base[dana_type.base]
    
    for num in dana_type.dims:
        if num and not no_arrays:
            t = ir.ArrayType(t, num)
        else:
            t = ir.PointerType(t)

    if dana_type.args is not None:
        t = ir.FunctionType(t, [irtype(arg) for arg in dana_type.args])
        
    return t

def irpointer(addr, dana_type, builder):
    if dana_type.dims and any(x for x in dana_type.dims): 
        return builder.bitcast(addr, irtype(dana_type, no_arrays = True))
    else:
        return addr
    
def irgen_string(string, builder):

    string_type = irtype(string.type) 
    addr = ir.GlobalVariable(builder.module, string_type, constant_names[string.value])
    addr.global_constant = True 
    addr.initializer = ir.Constant(string_type, bytearray(ord(c) for c in string.value))
    addr.unnamed_addr = True

    constant_names[expr.value] = irpointer(addr, expr.type, builder)



def irgen_expr(expr, builder, addr_table):
    operator = expr.operator

    if operator == "const":
        return ir.Constant(irtype(expr.type), int(expr.value))    
    elif operator == "call":
        name = expr.value
        args = [irgen_expr(arg, builder, addr_table) for arg in expr.children]
        return builder.call(function_table[name], args, name)
    elif operator == "lvalue":
        addr = irgen_lvalue(expr, builder, addr_table)
        return builder.load(addr)
    elif operator == "string":
        if not expr.value in constant_names:
            irgen_string(expr, builder)         
        return constant_names[expr.value]

    elif len(expr.children) == 1:
        operand = irgen_expr(expr.children[0], builder, addr_table)
        if operator == "id": 
            return irgen_expr(operand, builder, addr_table)
        elif operator == "neg": 
            return builder.neg(operand, builder, addr_table)
        elif operator == "!": 
            byte_one = ir.Constant(irtype["byte"], 0x1)
            last_byte = builder.and_(byte_one, operand)
            return builder.sub(byte_one, operand)
        elif operator == "not":
            return builder.not_(operand) 

    elif len(expr.children) == 2:
        first = irgen_expr(expr.children[0], builder, addr_table)
        second = irgen_expr(expr.children[1], builder, addr_table)
        if operator == "+":
            return builder.add(first, second) 
        elif operator == "-":
            return builder.sub(first, second) 
        elif operator == "*":
            return builder.mul(first, second) 
        elif operator == "/":
            return builder.div(first, second) 
        elif operator == "%":
            return builder.rem(first, second) 
        elif operator == "&":
            return builder.and_(first, second) 
        elif operator == "|":
            return builder.or_(first, second) 
        elif operator == "and":
            return builder.or_(first, second) 
        elif operator == "or":
            return builder.or_(first, second) 
        elif operator == "=":
            return builder.icmp_signed("==", first, second) 
        elif operator == "!=":
            return builder.icmp_signed("!=", first, second) 
        elif operator == "<":
            return builder.icmp_signed("<", first, second) 
        elif operator == "<=":
            return builder.icmp_signed("<=", first, second) 
        elif operator == ">=":
            return builder.icmp_signed(">=", first, second) 
        elif operator == ">":
            return builder.icmp_signed(">", first, second) 


def irgen_lvalue(lvalue, builder, addr_table):
    #TODO CHANGE FOR STATIC SCOPING
    addr = None
    
    assert lvalue.operator != "string"

    if lvalue.children:
        child = irgen_lvalue(lvalue.children[0], builder, addr_table)
        expr = irgen_expr(lvalue.value, builder, addr_table)
        addr = builder.gep(child, [expr]) 
    else:
        return addr_table[lvalue.value]

    return addr



def irgen_stmt(stmt, builder, addr_table):
    
    operator = stmt.operator
    if operator == "ret":
        if not stmt.exprs:
            return builder.ret_void()
        else:
            retval = irgen_expr(stmt.exprs[0], builder, addr_table)
            return builder.ret(retval) 
    elif operator == "continue":
        tmp = builder.unreachable()             
        if stmt.label:
            unpatched_cont[tmp] = (builder.block, addr_table[stmt.label])
        else:
            unpatched_cont[tmp] = (builder.block, None)
        return tmp
    elif operator == "break":
        tmp = builder.unreachable()             
        if stmt.label:
            unpatched_break[tmp] = (builder.block, addr_table[stmt.label])
        else:
            unpatched_break[tmp] = (builder.block, None) 
        return tmp
    elif operator == "call":
        args = [irgen_expr(expr, builder, addr_table) for expr in stmt.exprs]
        return builder.call(function_table[stmt.value], args)
    elif operator == "assign":
        lvalue = irgen_lvalue(stmt.exprs[0], builder, addr_table)
        expr = irgen_expr(stmt.exprs[1], builder, addr_table)
        return builder.store(expr, lvalue)
        
        
def irgen_block(func, block, addr_table):
    btype = block.type

    if btype == "container":
        blks = []
        children = []
        for child in block.children:
            previous = children
            children = irgen_block(func, child, addr_table)
            for blk in previous:
                if isinstance(blk.instructions[-1], ir.Unreachable) and \
                   blk.instructions[-1] in unpatched_next:
                    blk.replace(blk.instructions[-1], ir.Branch(blk, "br", [children[0]]))

            blks += children 

        return blks 
        

    if btype == "basic":
        blk = func.append_basic_block()
        builder = ir.IRBuilder(blk)
        
        for stmt in block.stmts:
            irgen_stmt(stmt, builder, addr_table)
                
        if not blk.is_terminated:
            tmp = builder.unreachable() 
            unpatched_next[tmp] = (builder.block, None)

        return [blk]

    elif btype == "loop": 
        blks = []

        entry = func.append_basic_block(block.label)
        

        blks = irgen_block(func, block.block, addr_table)

        entry_builder = ir.IRBuilder(entry)
        entry_builder.branch(blks[0])

        # In case the last block is unfinished
        exit = blks[-1]
        if isinstance(exit.instructions[-1], ir.Unreachable) and \
            exit.instructions[-1] in unpatched_next:
            exit.replace(exit.instructions[-1], ir.Branch(exit, "br", [entry])) 
        else:
            exit = func.append_basic_block()
            exit_builder = ir.IRBuilder(exit)
            exit_builder.branch(entry)
    
        for blk in blks:
            for inst in blk.instructions:
                if inst in unpatched_break:
                    (b, lab) = unpatched_break[inst]
                    if not lab or (block.label and lab == block.label):
                        unpatched_break.pop(inst)
                        unpatched_next[inst] = (b, lab)

                if inst in unpatched_cont:
                    (b, lab) = unpatched_cont[inst]
                    if not lab or (block.label and lab == block.label):
                        unpatched_cont.pop(inst)
                        b.replace(inst, ir.Branch(exit, "br", [entry])) 
                        

        return [entry] + blks + [exit]

    elif btype == "if":
        start = func.append_basic_block()
        builder = ir.IRBuilder(start)
        pred = irgen_expr(block.cond, builder, addr_table)


        temp = builder.unreachable()
        
        if_blks = irgen_block(func, block.if_path, addr_table)

        else_blks = []
        if block.else_path:
            else_blks += irgen_block(func, block.else_path, addr_table)
        else:
            else_blks = [func.append_basic_block()]
            else_builder = ir.IRBuilder(else_blks[0])
            tmp = else_builder.unreachable() 
            unpatched_next[tmp] = (builder.block, None)

        start.replace(temp, ir.ConditionalBranch(start, "br", [pred, if_blks[0], else_blks[0]]))
        
            

        return [start] + if_blks + else_blks 
             

    
def irgen_func(function, module, addr_table):
    name = function.symbol.name
    fnty = irtype(function.symbol.type)
    func = ir.Function(module, fnty, name = name)

    function_table[name] = func

    for arg, name in zip(func.args, [symbol.name for symbol in function.args]):
        arg.name = name

    entry = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry)
    for arg in func.args:
        #TODO CHANGE FOR STATIC SCOPING
        addr = builder.alloca(arg.type)
        builder.store(arg, addr)
        addr_table[arg.name] = addr

    for symbol in function.defs:
        addr = irpointer(builder.alloca(irtype(symbol.type)), symbol.type, builder)
        addr_table[symbol.name] = addr
        

    blks = irgen_block(func, function.block, addr_table)
    builder.branch(func.blocks[1])
    exit = func.append_basic_block(name="exit")
    builder = ir.IRBuilder(exit)
    builder.ret_void()
    
    for blk in blks:
        if isinstance(blk.instructions[-1], ir.Unreachable):
            blk.replace(blk.instructions[-1], ir.Branch(blk, "br", [exit]))

    for child in function.children:
        irgen_func(child, module, addr_table)
    

def irgen(main):
    
    module = ir.Module(name = "test.imm")
    module.triple = "x86_64-linux-gnu"
    addr_table = dict()
    for builtin in builtins:
        name = builtin.name
        fnty = irtype(builtin.type) 
        func = ir.Function(module, fnty, name = name)
        function_table[name] = func


    irgen_func(main, module, addr_table)
    print(module)


def test():
    try:
        program = open(sys.argv[1], 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        return
    lexer = lex()  
    yacc = parser(start='program')
    ast = yacc.parse(program.read(),tracking=True,debug=False)

    main_function = ast.children[0] 
    function = produce_program(main_function)           
    irgen(function)


if __name__ == "__main__":
    test()










    
    



