import sys
from copy import copy
from collections import deque as deque
from compiler.parser.lexer import lex as lex, tokens as tokens
from compiler.parser.parser import parser as parser
from compiler.semantic.semantic import produce_program as produce_program
from compiler.semantic.semantic import builtins as builtins
from compiler.codegen.expr import *
from compiler.codegen.block import irgen_block as irgen_block
from compiler.codegen.table import Table as Table
from llvmlite import ir as ir


    
def irgen_func(function, module, table):
    name = function.symbol.name
    fnty = irtype(function.symbol.type)
    func = ir.Function(module, fnty, name = name)

    table.funcs[name] = func

    for arg, name in zip(func.args, [symbol.name for symbol in function.args]):
        arg.name = name

    entry = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry)
    for arg in func.args:
        #TODO CHANGE FOR STATIC SCOPING
        addr = builder.alloca(arg.type)
        builder.store(arg, addr)
        table[arg.name] = addr

    for symbol in function.defs:
        addr = irpointer(builder.alloca(irtype(symbol.type)), symbol.type, builder)
        table[symbol.name] = addr
        

    blks = irgen_block(func, function.block, table)
    builder.branch(func.blocks[1])
    exit = func.append_basic_block(name="exit")
    builder = ir.IRBuilder(exit)
    if function.is_main and True:
        builder.call(table.funcs["exit"], [ir.Constant(ir.IntType(8), 0)])
        # Actually unreachable, but we do not explicitly denote it to avoid
        # optimizing the block out of existence
    builder.ret_void()
    
    for blk in blks:
        if isinstance(blk.instructions[-1], ir.Unreachable):
            blk.replace(blk.instructions[-1], ir.Branch(blk, "br", [exit]))

    for child in function.children:
        irgen_func(child, module, table)
    

def irgen(main): 
    module = ir.Module(name = "test.imm")
    module.triple = "x86_64-linux-gnu"
    table = Table()
    for builtin in builtins:
        name = builtin.name
        fnty = irtype(builtin.type) 
        func = ir.Function(module, fnty, name = name)
        table.funcs[name] = func


    irgen_func(main, module, table)
    
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
