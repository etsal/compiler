from collections import deque as deque
from helper.type import *
from helper.repr import * 
from copy import copy
import sys

from frontend.lexer import lex as lex, tokens as tokens
from frontend.parser import parser as parser

#Subtrees: <fpar-type> | <type> | <data-type>
#Subtree: <type> | "ref" <data-type> | <data-type> "[" "]" ("[" <int-const> "]")* 
def get_type(dana_type):
    base = dana_type.find_first("p_data_type").value    

    dims = list(const.value for const in  dana_type.find_all("p_number")) 
    if dana_type.find_first("p_empty_brackets"):
        dims = [0] + dims
      
    ref = True if dana_type.find_first("p_ref") else False
         
    return DanaType(base, dims = dims, ref = ref)


#Subtree: <id> ["is" <data-type>] [":" <fpar-def> (",", <fpar-def>)*]
# Traverse function header, extracting the type of the function it refers to
def get_function_symbol(dana_header):        
    name = dana_header.find_first("p_name").value

    base = dana_header.find_first("p_maybe_data_type").find_first("p_data_type")
    if base:
        base = base.value
    if not base:
        base = "void"
        
    args = list(map(get_type, dana_header.find_all("p_fpar_def")))

    return Symbol(name, DanaType(base, args = args))

        
#Subtree: (<id>)+ "as" <fpar-type> | "var" (<id>)+ "is" <type>
# Traverses both p_var_def and p_fpar_def tokens
def get_variable_symbols(dana_def):

    variables = dana_def.find_first("p_name")
    var_type = dana_def.find_first("p_dana_type")
    
    return [Symbol(var, var_type) for var in variables]
 

def produce_function(dana_function, parent = None, global_table = dict()):
    
    dana_header = dana_function.find_first("p_header")
    function = get_function_symbol(dana_header)
    dana_args = dana_header.find_all("p_fpar_def") 

    dana_local_def_list = dana_function.find_first_child("p_local_def_list")
    dana_local_defs = []
    if dana_local_def_list:
        dana_local_defs = dana_function.find_first("p_local_def_list").multifind(["p_func_def", "p_func_decl", "p_var_def"])

    local_table = dict()

    dana_block = dana_function.find_first("p_block")
    block = DanaBlock(dana_block) 


    args = []
    defs = []
    decls = []
    funcs = []
    
    function = DanaFunction(parent, function, defs, args, block)

    for local_def in dana_args + dana_local_defs:
        symbols = None
        if local_def.name in ["p_func_decl", "p_func_def"]:
            symbols = [get_function_symbol(local_def.find_first("p_header"))] 
            if local_def.name == "p_func_decl":
                decls += symbols

            elif local_def.name == "p_func_def":
                funcs += symbols
                
                temp_table = copy(global_table)
                for key in local_table.keys():
                    temp_table[key] = local_table[key]

                function.children.append(produce_function(local_def, function, temp_table))
                print(produce_function(local_def, function, temp_table))

        elif local_def.name in ["p_var_def", "p_fpar_def"]:
            names = map(lambda name: name.value, local_def.find_all("p_name"))
            symbols = [Symbol(name, get_type(local_def)) for name in names]   

            if local_def.name == "p_var_def":
                defs += symbols

            elif local_def.name == "p_fpar_def":
                args += symbols


        else:
            raise ValueError("Local definition is not declaration or definition")
        
        for symbol in symbols:
            if (symbol.name in local_table) and not (len([x for x in funcs if x.name == symbol.name]) == 1 and symbol.name in [decl.name for decl in decls]):
                print("Lines {}: Name {} already defined in current scope".format(dana_function.linespan, symbol.name))

            local_table[symbol.name] = symbol.type 
         

    return function

    
    

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
    function = produce_function(main_function)        
        
    print(function)

    return


if __name__ == "__main__":
    test()










    
    



