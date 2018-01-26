import sys
from copy import copy
from collections import deque as deque
from compiler.parser.lexer import lex as lex, tokens as tokens
from compiler.parser.parser import parser as parser
from compiler.semantic.semantic import produce_program as produce_program
from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.semantic import builtins as builtins
from compiler.codegen.expr import *
from compiler.codegen.block import irgen_block as irgen_block, backpatch as backpatch
from compiler.codegen.table import Table as Table
from llvmlite import ir as ir

def irgen_extern(module, symbol, table):
    name = symbol.name
    fnty = irtype(symbol.type)
    func = ir.Function(module, fnty, name=name)
    table.funcs[name] = func


def irgen_decl(module, function, table):
    fnty = irtype(function.symbol.type)
    func = ir.Function(module, fnty, name=function.mangled.name)

    table.funcs[function.symbol.name] = func
    return func
       

def irgen_args(function, builder, table):
    addrs = []
    for symbol in function.args:
        addr = irpointer(builder.alloca(irtype(symbol.type)), symbol.type, builder)
        table[symbol.name] = addr
        addrs.append(addr)
    return addrs

def irgen_defs(function, builder, table):
    for symbol in function.defs:
        # We may allocate an array type, but we always use a pointer type
        addr = irpointer(builder.alloca(irtype(symbol.type)), symbol.type, builder)
        table[symbol.name] = addr


def irgen_entry(func, function, table):
    # Entry block, where the allocations/initializations are
    entry = func.append_basic_block(name="entry")
    entry_builder = ir.IRBuilder(entry)
            
    

    irgen_defs(function, entry_builder, table)
    addrs = irgen_args(function, entry_builder, table)
    for arg, addr in zip(func.args, addrs):
        entry_builder.store(arg, addr) 

    entry_builder.unreachable()

    # Name the arguments for more readable IR (at least at first)
    for arg, name in zip(func.args, [symbol.name for symbol in function.args]):
        arg.name = name

    return entry

def irgen_exit(func, function, table):
    exit = func.append_basic_block(name="exit")
    exit_builder = ir.IRBuilder(exit)

    # If the function is actually main, we have to enter an exit syscall to
    # be able to terminate properly - we do not have support routines like
    # crto0, so we make our own
    if function.is_main:
        exit_builder.call(table.funcs["exit"], [ir.Constant(ir.IntType(8), 0)])

    if DanaType(function.symbol.type.base) == DanaType("void"):
    # Never reached for main, but used in void functions 
        exit_builder.ret_void() 
    else:
        exit_builder.unreachable()

    return exit

def child_table(function, table):
    new_table = Table()

    for name in function.parents:
        new_table[name] = table[name]

    new_table.funcs = copy(table.funcs)
    new_table.globals = copy(table.globals)
    new_table.counter = table.counter 

    return new_table


def irgen_func(module, function, table):
    func = irgen_decl(module, function, table)

    for child in function.children:
        new_table = child_table(child, table)
        child_func = irgen_func(module, child, new_table)
        table.funcs[child.symbol.name] = child_func
        table.counter = new_table.counter


    entry = irgen_entry(func, function, table)
    blks = irgen_block(func, function.block, table)
    exit = irgen_exit(func, function, table)
    
    # Backpatch entry block to point to the next one
    branch = ir.Branch(entry, "br", [blks[0]])
    backpatch(entry, branch)


    # Backpatch dangling blocks to point to the exit
    for blk in blks:
        if isinstance(blk.terminator, ir.Unreachable):
            branch = ir.Branch(blk, "br", [exit])
            backpatch(blk, branch)
 
    return func



def irgen(main): 
    module = ir.Module()
    module.triple = "x86_64-linux-gnu"
    table = Table()
    # Builtin declarations to be linked
    for builtin in builtins:
        irgen_extern(module, builtin, table)


    irgen_func(module, main, table)
    
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
