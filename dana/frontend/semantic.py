import sys
from collections import deque as deque
import copy
from frontend.lexer import lex as lex, tokens as tokens
from frontend.parser import parser as parser
from helper.tree import Node as Node  
from helper.type import DanaType as DanaType 
from helper.scope_stack import ScopeStack as ScopeStack
from helper.scope import Scope as Scope
from helper.extendleft import extendleft_no_reverse as extendleft_no_reverse
from helper.builtins import builtins as builtins
from frontend.symbolhelpers import *

stack = ScopeStack([Scope(symbols = builtins)])

def get_expr_type(dana_expr):
    first_token = dana_expr.children[0]

    # Subtree: "(" <expr> ")"
    if first_token == "(":
        return get_expr_type(dana_expr.children[1])

    #Subtree: ("+" | "-") <expr>
    elif first_token in ["+", "-"]:
        expr_type = get_expr_type(dana_expr.children[1])
        if expr_type != DanaType("int"):
            print("Unary sign operator applied to nonint expression")
        return expr_type

    #Subtree: "!" <expr>
    elif first_token == "!":
        expr_type = get_expr_type(dana_expr.children[1])
        if expr_type != DanaType("byte"):
            print("Negation operator ! applied to nonbyte expression")
        return expr_type

    #Subtree: <int-const>
    elif first_token.name == "p_number":
        return DanaType("int")
    
    #Subtree: <char-const>
    elif first_token.name == "p_char":
        return DanaType("byte")

    #Subtree: <lvalue>
    elif first_token.name == "p_string":
        return DanaType("byte", [0])

    #Subtree: "true" | "false"
    elif first_token.name == "p_boolean":
        return DanaType("logic")

    #Subtree: <lvalue>
    elif first_token.name == "p_lvalue":
        return get_lvalue_type(first_token) 

    #Subtree: <expr> ("+" | "-" | "*" | "/" | "%" ) <expr> | <expr> ("&" | "|") <expr>
    elif first_token.name == "p_expr":
        operation = dana_expr.children[1]

        #Subtree: <expr> ("+" | "-" | "*" | "/" | "%" ) <expr> 
        if operation in ["+", "-", "STAR", "SLASH", "PERCENT"]:
            
            op1_type = get_expr_type(dana_expr.children[0])
            op2_type = get_expr_type(dana_expr.children[2])
            if op1_type != op2_type:
                print("Type mismatch between expressions being compared. Types are {} and {}".format(op1_type, op2_type))
            elif op1_type not in [DanaType("int"), DanaType("byte")]:
                print("Arithmetic operation between expressions of that are not of type int or byte")
        
            return op1_type

        #Subtree: <expr> ("&" | "|") <expr>
        elif operation in ["&", "|"]:
            op1_type = get_expr_type(dana_expr.children[0])
            op2_type = get_expr_type(dana_expr.children[2])
            if op1_type != DanaType("byte") or op1_type != DanaType("byte"):
                print("Logical operation between expressions that are not of type byte")
        
            return DanaType("logic")

    #Subtree: <func-call>
    elif first_token.name == "p_func_call":
        function_name = first_token.children[0].value
        if not stack.name_in_stack(function_name):
            print("Process {} not defined".format(function_name))
        call_ops = get_call_ops(dana_expr)

        if stack.name_type(function_name).ops != call_ops:
            print("Function {} not called with proper arguments".format(first_token.children[0].value))
        
        return stack.name_type(function_name)


def verify_cond(dana_cond):
    first_token = dana_cond.children[0]

    #Subtree: "(" <cond> ")"
    if first_token == "(":
        verify_cond(dana_cond.children[1])

    #Subtree: "not" <cond>
    elif first_token == "not":
        verify_cond(dana_cond.chilren[1])


    #Subtree: <cond> ("and" | "or") <cond>
    elif first_token == "p_cond":
        verify_cond(dana_cond.children[0])
        verify_cond(dana_cond.children[2])

    #Subtree: <expr> | <expr> ("=" | "<>" | "<" | ">" | "<=" | ">=") <expr>
    elif first_token.name == "p_expr":
        #Subtree: <expr> 
        if len(dana_cond.children) == 1:
            expr_type = get_expr_type(first_token)
            if expr_type != DanaType("logic"):
                print("Expression used in condition has no truth value")
        #Subtree: <expr> ("=" | "<>" | "<" | ">" | "<=" | ">=") <expr>
        else:
            op1_type = get_expr_type(dana_cond.children[0])
            op2_type = get_expr_type(dana_cond.children[2])
            if op1_type != op2_type:
                print("Type mismatch between expressions being compared. Types are {} and {}".format(op1_type, op2_type))
            elif op1_type not in [DanaType("int"), DanaType("byte")]:
                print("Comparison between expressions of a nonordered type")
                    


def verify_statement(dana_statement):
    first_token = dana_statement.children[0]


    #Subtree: "skip"
    if first_token == "skip":
        pass 

    #Subtree: "exit" | "return" ":" <expr> 
    elif first_token == "return" or first_token == "exit":
        #Subtree: "return" ":" <expr> 
        if first_token == "return":
            return_expression = dana_statement.children[2]
            return_type = get_expr_typeession(return_expression)
        #Subtree: "exit"
        else:
            return_type = DanaType("void")

        current_function = stack.top_function()
        if return_type != current_function[1]:
            print("Type mismatch: Function {} returns {}, but return expression is of type {}"
                        .format(current_function[0], current_function[1], return_type))
        

    #Subtree: "if" <cond> ":" <block> ("elif" <cond> ":" <block>)* ["else" ":" <block> ]
    elif first_token == "if":
        verify_if_statement(dana_statement)


    #Subtree: "loop" [<id>] ":" <block> 
    elif first_token == "loop":
        # If there is a label, store it
        if len(dana_statement.children) == 4:
            this.stack.push_symbol((dana_statement.children[1].value, DanaType("label")))

        looped_block = dana_statement.children[-1]
        verify_block(looped_block)


    #Subtree: "break" [":" <id>] | "continue" [":" <id>]
    # These two are handled identically at a semantic level
    elif first_token == "break" or first_token == "continue":
        if len(dana_statement.children) > 1:
            label_name = dana_statement.children[2].value
            if not scope.in_stack(label_name):
                print("Label not found: {}".format(label_name))
            symbol_type = stack.first_type(label_name)

            if symbol_type is None:
                print("Label named {} not found!".format(label_name))
                return

            if symbol_type != DanaType("label"):
                print("Nonlabel id {} used as label".format(label_name))
                    

    #Subtree: <lvalue> ":=" <expr>
    elif first_token.name == "p_lvalue":
       lvalue_type = get_lvalue_type(dana_statement.children[0]) 
       expr_type = get_expr_type(dana_statement.children[2]) 

       if lvalue_type != expr_type:
            print("Line {}: ".format(dana_statement.linespan), end="")
            print("Lvalue is of type {}, but is assigned an expression of type {}".format(lvalue_type, expr_type))


    #Subtree: <proc-call>
    # Procs are have return type void by design, so no need to check that
    elif first_token.name == "p_proc_call":
            
        process_name = first_token.children[0].value
        if not stack.name_in_stack(process_name):
            print("Process {} not defined".format(process_name))
        definition_type = stack.name_type(process_name) 
        call_type = DanaType("void", ops = get_call_ops(dana_statement))

        if definition_type != call_type:
            print("Problem by process call {}".format(first_token.children[0].value))
            print("Expected type: {}".format(definition_type))
            print("Found type: {}".format(call_type))
            

             
#Subtree: "if" <cond> ":" <block> ("elif" <cond> ":" <block>)* ["else" ":" <block> ]
def verify_if_statement(dana_if_statement):
    unprocessed = deque(dana_if_statement.children)
    while unprocessed:
        child = unprocessed.popleft()
        if isinstance(child, str):
            continue
        #Subtree: <cond>
        if child.name == "p_cond":
            verify_cond(child)


        #Subtree: <block>
        elif child.name == "p_block": 
            verify_block(child)


        else:
            extendleft_no_reverse(unprocessed, child.children)     

#Subtree: <id> | <string-literal> | <lvalue> "[" <expr> "]"
def get_lvalue_type(dana_lvalue):
    first_token = dana_lvalue.children[0]
    #Subtree: <id>
    if first_token.name == "p_name":
        if not stack.name_in_stack(first_token.value):
            print("Symbol {} not defined!".format(name))
      
        return copy.deepcopy(stack.name_type(first_token.value)) 
    #WARNING: NEED TO HANDLE <string-literal>
    #Subtree <lvalue> "[" <expr> "]"
    else:
        
        base_type = get_lvalue_type(first_token) 
        expr_type = get_expr_type(dana_lvalue.children[2])
        if expr_type != DanaType("int"):
            print("Expression used as index is of type {}".format(expr_type))
        if not base_type.dims:
            print("Nonarray lvalue dereferenced") 
        base_type.dims= base_type.dims[:-1]
        return base_type
         

#Subtree: <id> [":" <expr> ("," <expr)*] | <id> "(" [<expr> ("," <expr>)*] ")"
def get_call_ops(dana_call):
    call_ops = []
    unprocessed = deque(dana_call.children)
    while unprocessed:
        child = unprocessed.popleft()
        if isinstance(child, str):
            continue
        #Subtree: <expr>
        if child.name == "p_expr":
            call_ops += [get_expr_type(child)]

        else:
            extendleft_no_reverse(unprocessed, child.children) 

    
    return call_ops


# Traverse statement block, checking its symbols against the current stack
def verify_block(dana_block):

    unprocessed = deque([dana_block])
    while unprocessed:
        child = unprocessed.popleft()
        #For "begin", "end"    
        if isinstance(child, str):
            continue

        #For "stmt"
        elif child.name == "p_stmt":
            verify_statement(child) 

        else:
            extendleft_no_reverse(unprocessed, child.children)


def produce_scope(dana_function):

    function_header = dana_function.children[1]
    current_function = get_function_symbol(function_header)
    scope = Scope(current_function)

    unprocessed = deque(dana_function.children)
    while unprocessed:
        child = unprocessed.popleft()

        # In order to avoid AttributeError exceptions, and therefore 
        # having to ignore them altogether
        if isinstance(child, str):
            continue

        # If we just find a p_fpar_def token, that means that it's a parameter of the 
        # function being traversed. Likewise, if we find a p_var_def token, it's a 
        # local definition

        elif child.name == "p_var_def" or child.name == "p_fpar_def":
            symbols = get_variable_symbols(child)
            for symbol in symbols:
                symbol_name = symbol[0]
                if scope.name_in_scope(symbol_name):
                    print("Symbol {} already defined in current scope!".format(symbol))
                
            scope.push_symbols(symbols)    

        elif child.name == "p_func_decl" or child.name == "p_func_def":                     
            
            func_header = child.children[1] 
            func_symbol = get_function_symbol(func_header)                                         
            func_name = func_symbol[0]

            if scope.name_in_scope(func_name):
                print("Symbol {} already defined in current scope!".format(func_symbol))

            scope.push_symbol(func_symbol)

            # If child is a full function definition, check its semantics, too
            if child.name == "p_func_def":
                # Temporarily add the current scope, so that the variables are visible 
                # to the inner function being verified
                stack.add_scope(scope)
                verify_function(child)
                stack.pop_scope()

        # Once we reach the block, we cannot find any more definitions
        elif child.name == "p_block":
            break

        else:
            extendleft_no_reverse(unprocessed, child.children)
            

    return scope

def verify_function(dana_function):
    stack.add_scope(produce_scope(dana_function))
    function_block = dana_function.children[-1]
    verify_block(function_block)
    stack.pop_scope()



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
    verify_function(main_function)        
        
    return


if __name__ == "__main__":
    test()
