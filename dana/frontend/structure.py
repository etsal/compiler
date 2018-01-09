from collections import deque as deque
from helper.type import *
from helper.repr import * 
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

    base = dana_header.find_first_child("p_data_type")
    if not base:
        base = "void"
        
    args = map(get_type, dana_header.find_all("p_fpar_def"))     

    return Symbol(name, DanaType(base, args = args))

        
#Subtree: (<id>)+ "as" <fpar-type> | "var" (<id>)+ "is" <type>
# Traverses both p_var_def and p_fpar_def tokens
def get_variable_symbols(dana_def):

    variables = dana_def.find_first("p_name")
    var_type = dana_def.find_first("p_dana_type")
    
    return [Symbol(var, var_type) for var in variables]
 

def produce_function(dana_function, parent = None):
    
    dana_header = dana_function.find_first("p_header")
    dana_args = dana_header.find_all("p_fpar_def") 

    function = get_function_symbol(dana_header)

    dana_local_def_list = dana_function.find_first_child("p_local_def_list")
    dana_local_defs = dana_local_def_list.multifind(["p_func_def", "p_func_decl", "p_var_def"])
    dana_block = dana_function.find_first("p_block")

    dana_defs = [local_def for local_def in dana_local_defs if local_def.name == "p_var_def"]
    dana_funcs = [local_def for local_def in dana_local_defs if local_def.name != "p_var_def"]

    defs = []
    for dana_def in dana_defs:
        names = map(lambda name: name.value, dana_def.find_all("p_name"))
        dana_type = get_type(dana_def)
        defs += [Symbol(name, dana_type) for name in names]   

    args = []
    for dana_arg in dana_args:
        names = map(lambda name: name.value, dana_arg.find_all("p_name"))
        dana_type = get_type(dana_arg)
        args += [Symbol(name, dana_type) for name in names]   

    
    funcs = [get_function_symbol(function) for function in dana_funcs]
    
    block = DanaBlock(dana_block) 

    return DanaFunction(parent, function, defs, args, block)

    
    

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










    
    



