import sys
from copy import copy
from compiler.parser.lexer import lex, tokens
from compiler.parser.parser import parser
from compiler.semantic.semantic import produce_program
from compiler.semantic.table import Symbol
from compiler.semantic.type import DanaType
from compiler.semantic.semantic import builtins
from compiler.codegen.type import irtype
from compiler.codegen.block import irgen_block, backpatch
import compiler.codegen.table as irtable
from llvmlite import ir

def irgen_decl(module, symbol, mangled, table):
    # Only base return types allowed, so we just use the base
    base = irtype(symbol.type.base)

    # Turn all array arguments to pointers
    argtypes = [irtype(arg.base, len(arg.dims) + arg.pdepth, []) \
                    for arg in symbol.type.args]
    # If passed by reference, we turn it into a pointer type
    for i, arg in enumerate(symbol.type.args):
        if arg.is_ref:
            argtypes[i] = ir.PointerType(argtypes[i])
    fnty = ir.FunctionType(base, argtypes)
    func = ir.Function(module, fnty, name=mangled.name)

    # Add relevant entries in the global and local tables
    table.mangles[symbol.name] = mangled.name
    # Incomplete entry in case there are extra args
    table.funcs[mangled.name] = irtable.FuncInfo(func, [])

    return func

def irgen_def(module, function, table):

    # We have a variety of options on how to access variables from
    # upper scopes; the solution we choose is the one of llvm-gcc -
    # pass the needed variables as arguments (llvm-gcc passes a struct,
    # but that is not a big difference)
    extra_args = list(function.table.referenced)
    extra_types = list(function.table[arg] for arg in extra_args)

    # All items from outer scopes are passed by reference
    for extra_type in extra_types:
        if not extra_type.is_array and not extra_type.is_pointer:
            extra_type.is_ref = True

    function.symbol.type.args += extra_types
    function.table.extend_args([Symbol(arg, t) for arg, t in zip(extra_args, extra_types)])

    func = irgen_decl(module, function.symbol, function.mangled, table)

    # Get all upper-scoped variables, turn arrays to pointers
    dtype = function.mangled.type
    argtypes = [function.table[arg] for arg in extra_args]
    dtype.args += argtypes


    # Name the arguments for more readable IR (at least at first)
    for arg, name in zip(func.args, function.args + extra_args):
        arg.name = name


    # Fix the incomplete entry
    mangled = function.mangled.name
    table.funcs[mangled] = irtable.FuncInfo(func, extra_args)
    table.current = mangled

    return func


# Pointers _always_ before array dimensions, there are no arrays
# of pointers
def irarray(dtype, builder):
    base = dtype.base
    dims = dtype.dims
    pdepth = dtype.pdepth
    if len(dims) > 1:
        # Get the outer array
        arrlen, *rest = dims
        arrtyp = irtype(base, pdepth + len(rest), [arrlen])
        arraddr = builder.alloca(arrtyp)
        arraddr = builder.bitcast(arraddr, irtype(base, pdepth + len(dims), []))
        # Build the inner arrays
        for i in range(arrlen):
            arrtype = DanaType(base, pdepth=pdepth, dims=dims[1:])
            addr = irarray(arrtype, builder)
            staddr = builder.gep(arraddr, [ir.Constant(ir.IntType(32), i)])
            builder.store(addr, staddr)
        return arraddr
    # Simple array
    elif dims:
        # Just allocate a variable
        base = irtype(base)
        size = dims[0]
        arrtyp = ir.ArrayType(base, size)
        arraddr = builder.alloca(arrtyp)
        addr = builder.bitcast(arraddr, ir.PointerType(base))
        return addr
    else:
        arrtyp = irtype(base)
        return builder.alloca(arrtyp)



def irdef(dtype, builder):
    if not dtype.is_array:
        arrtyp = irtype(dtype.base)
        return builder.alloca(arrtyp)

    return irarray(dtype, builder)


def irarg(arg, dtype, builder):
    if dtype.is_pointer or dtype.is_array or dtype.is_ref:
        return arg

    arrtyp = irtype(dtype.base)
    addr = builder.alloca(arrtyp)
    builder.store(arg, addr)
    return addr



def irgen_intro(func, function, table):
    # Entry block, where the allocations/initializations are
    intro = func.append_basic_block(name="intro")
    intro_builder = ir.IRBuilder(intro)

    for ddef in function.defs:
        table[ddef] = irdef(function.table[ddef], intro_builder)

    for darg, arg in zip(function.args, func.args):
        table[darg] = irarg(arg, function.table[darg], intro_builder)

    intro_builder.unreachable()
    return intro


def irgen_outro(func, function, table):
    outro = func.append_basic_block(name="outro")
    outro_builder = ir.IRBuilder(outro)

    # If the function is actually main, we have to enter an outro syscall to
    # be able to terminate properly - we do not have support routines like
    # crto0, so we make our own
    if function.is_main:
        outro_builder.call(table.funcs["exit"].func, [ir.Constant(ir.IntType(8), 0)])

    if DanaType(function.symbol.type.base) == DanaType("void"):
    # Never reached for main, but used in void functions
        outro_builder.ret_void()
    else:
        outro_builder.unreachable()

    return outro



def child_table(function, table):
    new_table = irtable.AddressTable(table.gtable)
    new_table.mangles = copy(table.mangles)
    return new_table


def irgen_func(module, function, table):
    func = irgen_def(module, function, table)

    for child in function.children:
        table.mangles[child.symbol.name] = child.mangled.name
        new_table = child_table(child, table)
        irgen_func(module, child, new_table)


    intro = irgen_intro(func, function, table)
    blks = irgen_block(func, function.block, table)
    outro = irgen_outro(func, function, table)

    # Backpatch intro block to point to the next one
    branch = ir.Branch(intro, "br", [blks[0]])
    backpatch(intro, branch)


    # Backpatch dangling blocks to point to the outro
    for blk in blks:
        if isinstance(blk.terminator, ir.Unreachable):
            branch = ir.Branch(blk, "br", [outro])
            backpatch(blk, branch)

    return func



def irgen(main):
    module = ir.Module()
    module.triple = "x86_64-linux-gnu"

    gtable = irtable.GlobalTable()
    table = irtable.AddressTable(gtable)
    # Builtin declarations to be linked
    for builtin in builtins:
        irgen_decl(module, builtin, builtin, table)

    irgen_func(module, main, table)

    return module

def test():
    try:
        program = open(sys.argv[1], 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        return
    lexer = lex()
    yacc = parser(start='program')
    ast = yacc.parse(program.read(), tracking=True, debug=False)

    main_function = ast.children[0]
    function = produce_program(main_function)
    irgen(function)


if __name__ == "__main__":
    test()
