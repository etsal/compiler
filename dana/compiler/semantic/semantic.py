import sys
from copy import copy
from compiler.parser.lexer import lex as lex, tokens as tokens
from compiler.parser.parser import parser as parser
from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.symbol import Symbol as Symbol
from compiler.semantic.table import Table as Table
from compiler.semantic.func import DanaFunction as DanaFunction
from compiler.semantic.block import DanaContainer as DanaContainer
from compiler.semantic.error import *

builtins = [
    Symbol("writeInteger", DanaType("void", args=[DanaType("int")])),
    Symbol("writeByte", DanaType("void", args=[DanaType("byte")])),
    Symbol("writeChar", DanaType("void", args=[DanaType("byte")])),
    Symbol("writeString", DanaType("void", args=[DanaType("byte", [0])])),
    Symbol("readInteger", DanaType("int", args=[])),
    Symbol("readByte", DanaType("byte", args=[])),
    Symbol("readChar", DanaType("byte", args=[])),
    Symbol("readString", DanaType("byte", [0], args=[])),
    Symbol("strlen", DanaType("int", args=[DanaType("byte", [0])])),
    Symbol("strcmp", DanaType("int", args=[DanaType("byte", [0]), DanaType("byte", [0])])),
    Symbol("strcat", DanaType("byte", [0], args=[DanaType("byte", [0]), DanaType("byte", [0])])),
    Symbol("strcpy", DanaType("byte", [0], args=[DanaType("byte", [0]), DanaType("byte", [0])])),
    Symbol("extend", DanaType("int", args=[DanaType("byte")])),
    Symbol("shrink", DanaType("byte", args=[DanaType("int")])),
    Symbol("exit", DanaType("void", args=[DanaType("byte")])),
]



#Subtrees: <fpar-type> | <type> | <data-type>
#Subtree: <type> | "ref" <data-type> | <data-type> "[" "]" ("[" <int-const> "]")*
def get_type(d_type):
    base = d_type.find_first("p_data_type").value

    dims = list(const.value for const in  d_type.find_all("p_number"))
    if d_type.find_first("p_empty_brackets"):
        dims = [0] + dims

    ref = True if d_type.find_first("p_ref") else False

    return DanaType(base, dims=dims, ref=ref)



#Subtree: <id> ["is" <data-type>] [":" <fpar-def> (",", <fpar-def>)*]
# Traverse function header, extracting the type of the function it refers to
def get_function_symbol(d_function):
    d_header = d_function.find_first("p_header")
    name = d_header.find_first("p_name").value

    base = d_header.find_first("p_maybe_data_type").find_first("p_data_type")
    if base:
        base = base.value
    if not base:
        base = "void"

    args = list(map(get_type, d_header.find_all("p_fpar_def")))

    return Symbol(name, DanaType(base, args=args))



#Subtree: (<id>)+ "as" <fpar-type> | "var" (<id>)+ "is" <type>
# Traverses both p_var_def and p_fpar_def tokens
def get_variable_symbols(d_def):
    variables = d_def.find_first("p_name")
    var_type = d_def.find_first("p_d_type")
    return [Symbol(var, var_type) for var in variables]


def get_function_variables(d_function):
    # Find all subtrees with definitions/declarations
    d_header = d_function.find_first("p_header")
    d_args = d_header.find_all("p_fpar_def")

    d_local_def_list = d_function.find_first_child("p_local_def_list")
    d_local_defs = []
    if d_local_def_list:
        d_local_defs = d_function.find_first("p_local_def_list") \
                                       .multifind(["p_func_def", "p_func_decl", "p_var_def"])

    return d_args + d_local_defs


def produce_function(d_function, parent=None, global_table=Table(), is_main=False):

    function = get_function_symbol(d_function)

    local_table = copy(global_table)
    local_table.function = function

    register = dict({"p_var_def" : local_table.extend_defs,
                     "p_var_decl" : local_table.extend_decls,
                     "p_var_arg" : local_table.extend_args,
                     "p_var_func" : local_table.extend_funcs,
                   })
    
    function = DanaFunction(parent, local_table, block=None)

    # Main isn't actually a function
    function.is_main = is_main
    if is_main:
        local_table[function.symbol.name] = function.symbol.type

    for local_def in get_function_variables(d_function):
        symbols = None
        if local_def.name in ["p_func_decl", "p_func_def"]:
            symbols = [get_function_symbol(local_def)]

        elif local_def.name in ["p_var_def", "p_fpar_def"]:
            names = map(lambda name: name.value, local_def.find_all("p_name"))
            symbols = [Symbol(name, get_type(local_def)) for name in names]

        else:
            raise ValueError("Local definition is not declaration or definition")



        for symbol in symbols:
            if (symbol.name in local_table) and \
                not (len([x for x in local_table.funcs if x.name == symbol.name]) == 1 and \
                    symbol.name in [decl.name for decl in local_table.decls]):
                print("Lines {}: Name {} already defined in current scope"
                      .format(d_function.linespan, symbol.name))

        register[local_def.name](symbols)

        if local_def.name == "p_func_def":
            temp_table = copy(local_table)
            new_function = produce_function(local_def, function, temp_table)
            function.children.append(new_function)


    d_block = d_function.find_first_child("p_block")
    function.block = DanaContainer(local_table, d_block=d_block)


    return function



def produce_program(main_function):
    global_table = Table()
    for symbol in builtins:
        global_table[symbol.name] = symbol.type

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
