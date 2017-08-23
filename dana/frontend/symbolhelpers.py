from collections import deque as deque
from helper.tree import Node as Node  
from helper.type import DanaType as DanaType 
from helper.extendleft import extendleft_no_reverse as extendleft_no_reverse


def get_primitive_data_type(dana_data_type):
    if dana_data_type.value == "int":
        return "int"

    elif dana_data_type.value == "byte":
        return "byte"


def get_total_data_type(dana_type):
    
    dims = []
    unprocessed = deque(dana_type.children)
    while unprocessed:
        child = unprocessed.popleft()

        if isinstance(child, str):
            continue
        
        elif child.name == "p_data_type":
            base = get_primitive_data_type(child)

        elif child.name == "p_number":
            dims += [child.value]  

        else:
           extendleft_no_reverse(unprocessed, child.children)

    return DanaType(base, dims = dims) 
    

def get_fpar_data_type(dana_fpar_type):
    first_token = dana_fpar_type.children[0]
    total_type = None

    if first_token.name == "p_ref":
        base_type = dana_fpar_type.children[1]
        total_type = DanaType(get_primitive_data_type(base_type), ref = True)

    elif first_token.name == "p_type":
        total_type = get_total_data_type(child)
        
    if total_type is not None:
        return total_type

    dims = []
    unprocessed = deque(dana_fpar_type.children)
    while unprocessed:
        child = unprocessed.popleft()

        if isinstance(child, str):
            continue        

        elif child.name == "p_data_type":
            base = get_primitive_data_type(child)

        elif child.name == "p_empty_brackets":                
             dims += [0]
    
        elif child.name == "p_number":
             dims += [number]
 
        else:
           extendleft_no_reverse(unprocessed, child.children)

    total_type = DanaType(base, dims = dims)
    return total_type


# Traverse function header, extracting the type of the function it refers to
def get_function_symbol(dana_header):        
    function_name = None
    function_type = "void"
    argument_types = []

    unprocessed = deque(dana_header.children)
    while unprocessed:
        child = unprocessed.popleft()

        if isinstance(child, str):
            continue
        
        if child.name == "p_name":
            function_name = child.value

        elif child.name == "p_data_type":
            function_type = get_primitive_data_type(child)

        # We just get the type of the parameter
        elif child.name == "p_fpar_def":
            argument_types += [y for (x,y) in get_variable_symbols(child)] 

        else:
            extendleft_no_reverse(unprocessed, child.children)

    return (function_name, DanaType(function_type, ops = argument_types))

        
# Traverses both p_var_def and p_fpar_def tokens
def get_variable_symbols(dana_def):
    symbols = deque() 
    unprocessed = deque(dana_def.children)
    while unprocessed:
        child = unprocessed.popleft()

        if isinstance(child, str):
            continue

        elif child.name == "p_name":
           symbols.append(child.value)

        elif child.name == "p_type":
           symbol_type = get_total_data_type(child) 

        elif child.name == "p_fpar_type":
           symbol_type = get_fpar_data_type(child)

        else:
           extendleft_no_reverse(unprocessed, child.children)
            

    return [(symbol, symbol_type) for symbol in symbols]

