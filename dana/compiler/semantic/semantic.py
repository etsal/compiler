import sys
from copy import copy
from compiler.parser.lexer import lex as lex, tokens as tokens
from compiler.parser.parser import parser as parser
from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.symbol import Symbol as Symbol
from compiler.semantic.table import Table as Table
from compiler.semantic.func import DanaFunction as DanaFunction
from compiler.semantic.block import DanaContainer as DanaContainer

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
]



#Subtrees: <fpar-type> | <type> | <data-type>
#Subtree: <type> | "ref" <data-type> | <data-type> "[" "]" ("[" <int-const> "]")*
def get_type(d_type):
    base = d_type.find_first("p_data_type").value

    dims = list(const.value for const in  d_type.find_all("p_number"))

    pdepth = 0
    if d_type.find_first("p_empty_brackets"):
        pdepth = 1 
        
    is_ref = True if d_type.find_first("p_ref") else False

    return DanaType(base, dims=dims, pdepth=pdepth, is_ref=is_ref)



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

    args = []
    fpars = d_header.find_all("p_fpar_def")
    for fpar in fpars:
        ftype = get_type(fpar.find_first("p_fpar_type"))
        args += [ftype] * len(fpar.find_all("p_name"))

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

    function_symbol = get_function_symbol(d_function)

    local_table = copy(global_table)
    local_table.function = function_symbol

    register = dict({"p_var_def" : local_table.extend_defs,
                     "p_fpar_def" : local_table.extend_args,
                     "p_func_def" : local_table.extend_funcs,
                     "p_func_decl" : local_table.extend_decls,
                   })
    
    stype = dict({"p_var_def" : "def", 
                  "p_fpar_def" : "arg", 
                  "p_func_def" : "func",
                  "p_func_decl" : "decl",
                })

    function = DanaFunction(parent, local_table, block=None)

    # Main isn't actually a function
    function.is_main = is_main
    if not is_main:
        local_table[function_symbol.name] = function_symbol.type

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
               (local_table.stype[symbol.name] != "parent") and \
                not (len([x for x in function.funcs if x == symbol.name]) == 1 and \
                    symbol.name in [decl.name for decl in local_table.decls]):
                raise ScopeError("Lines {}: Name {} already defined in current scope"
                      .format(d_function.linespan, symbol.name))

        register[local_def.name](symbols)

        if local_def.name == "p_func_def":
            child_table = copy(local_table)
            new_function = produce_function(local_def, function, child_table)
            function.children.append(new_function)

            # We get all values that are referenced from inner scopes, and 
            # note the ones that are not in an upper scope related to us 
            for name in new_function.table.referenced:
                if local_table.stype[name] == "parent":
                    local_table.referenced.add(name)

    d_block = d_function.find_first_child("p_block")
    function.block = DanaContainer(local_table, d_block=d_block)

    return function



def produce_program(main_function):
    global_table = Table()
    global_table.function = (None, DanaType("void"))
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
