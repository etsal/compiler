import sys
from copy import copy
from compiler.parser.lexer import lex, tokens
from compiler.parser.parser import parser
from compiler.semantic.type import DanaType
from compiler.semantic.table import Table, Symbol
from compiler.semantic.func import DanaFunction
from compiler.semantic.block import DanaContainer

builtins = [
    Symbol("writeInteger", DanaType("void", args=[DanaType("int")])),
    Symbol("writeByte", DanaType("void", args=[DanaType("byte")])),
    Symbol("writeChar", DanaType("void", args=[DanaType("byte")])),
    Symbol("writeString", DanaType("void", args=[DanaType("byte", pdepth=1)])),
    Symbol("readInteger", DanaType("int", args=[])),
    Symbol("readByte", DanaType("byte", args=[])),
    Symbol("readChar", DanaType("byte", args=[])),
    Symbol("readString", DanaType("void", args=[DanaType("int"), DanaType("byte", pdepth=1)])),
    Symbol("strlen", DanaType("int", args=[DanaType("byte", pdepth=1)])),
    Symbol("strcmp", DanaType("int", args=[DanaType("byte", pdepth=1), DanaType("byte", pdepth=1)])),
    Symbol("strcat", DanaType("byte", pdepth=1, args=[DanaType("byte", pdepth=1), DanaType("byte", pdepth=1)])),
    Symbol("strcpy", DanaType("byte", pdepth=1, args=[DanaType("byte", pdepth=1), DanaType("byte", pdepth=1)])),
    Symbol("extend", DanaType("int", args=[DanaType("byte")])),
    Symbol("shrink", DanaType("byte", args=[DanaType("int")])),
    Symbol("exit", DanaType("void", args=[DanaType("byte")])),
    Symbol("raise", DanaType("void", args=[DanaType("int")])),
]



def get_type(d_type):
    base = d_type.find_first("p_data_type").value
    dims = list(const.value for const in  d_type.find_all("p_number"))
    pdepth = 1 if d_type.find_first("p_empty_brackets") else 0
    is_ref = True if d_type.find_first("p_ref") else False
    return DanaType(base, dims=dims, pdepth=pdepth, is_ref=is_ref)



def get_function_symbol(d_function):
    """Get the name, type, and argument types of a function"""
    d_header = d_function.find_first("p_header")
    name = d_header.find_first("p_name").value

    d_type = d_header.find_first("p_maybe_data_type").find_first("p_data_type")
    base = d_type.value if d_type else "void"

    args = []
    fpars = d_header.find_all("p_fpar_def")
    for fpar in fpars:
        ftype = get_type(fpar.find_first("p_fpar_type"))
        args += [ftype] * len(fpar.find_all("p_name"))

    return Symbol(name, DanaType(base, args=args))


def check_and_register(local_def, table):
    stypes = dict({"p_var_def" : "def",
                   "p_fpar_def" : "arg",
                   "p_func_def" : "func",
                   "p_func_decl" : "decl",
                  })

    register = dict({"p_var_def" : table.extend_defs,
                     "p_fpar_def" : table.extend_args,
                     "p_func_def" : table.extend_funcs,
                     "p_func_decl" : table.extend_decls,
                    })
    symbols = None

    stype = stypes[local_def.name]
    if stype in ["func", "decl"]:
        symbols = [get_function_symbol(local_def)]

    elif stype in ["def", "arg"]:
        names = map(lambda name: name.value, local_def.find_all("p_name"))
        symbols = [Symbol(name, get_type(local_def)) for name in names]


    # Check for conflicts before registering the new symbols
    for name in map(lambda symbol: symbol.name, symbols):
        table.check_conflicts(local_def.linespan, name, stype)

    register[local_def.name](symbols)


def create_child(local_def, function, table):
    # Create the new function
    child_table = copy(table)
    new_function = produce_function(local_def, function, child_table)
    function.children.append(new_function)

    # Get all values that are referenced from inner scopes and not defined here
    for name in new_function.table.referenced:
        if table.stype[name] == "parent":
            table.referenced.add(name)


def produce_function(d_function, parent=None, global_table=Table(), is_main=False):

    table = copy(global_table)
    table.function = get_function_symbol(d_function)
    function = DanaFunction(parent, table, block=None)

    # Main isn't actually a function, so it has no symbol
    function.is_main = is_main
    if not is_main:
        table[table.function.name] = table.function.type


    local_defs = d_function.multifind(["p_fpar_def",
                                       "p_func_def",
                                       "p_func_decl",
                                       "p_var_def",
                                      ])
    for local_def in local_defs:
        check_and_register(local_def, table)

        if local_def.name == "p_func_def":
            create_child(local_def, function, table)

    d_block = d_function.find_first_child("p_block")
    function.block = DanaContainer(table, d_block=d_block)

    return function



def produce_program(main_function):
    global_table = Table()
    global_table.function = Symbol(None, DanaType("void"))
    global_table.extend_funcs(builtins)

    return produce_function(main_function, global_table=global_table, is_main=True)



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
    produce_program(main_function)

    return


if __name__ == "__main__":
    test()
