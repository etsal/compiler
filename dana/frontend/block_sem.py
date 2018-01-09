import sys
from copy import copy
from collections import deque as deque
from frontend.lexer import lex as lex, tokens as tokens
from frontend.parser import parser as parser
from helper.node import Node as Node  
from helper.type import DanaType as DanaType 
from helper.repr import * 
from helper.extendleft import extendleft_no_reverse as extendleft_no_reverse
from helper.builtins import builtins as builtins


def get_expr_type(dana_expr, symbol_table):
    return DanaType("byte")
    first_token = dana_expr.children[0]

    # Subtree: "(" <expr> ")"
    if first_token == "(":
        expr_token = dana_expr.children[1]
        return get_expr_type(expr_token)

    #Subtree: ("+" | "-") <expr>
    elif first_token in ["+", "-"]:
        expr_token = dana_expr.children[1]
        expr_type = get_expr_type(expr_token)
        if expr_type != DanaType("int"):
            print("Lines {}: ".format(dana_expr.linespan), end="")
            print("Unary sign operator applied to nonint expression")
        return expr_type

    #Subtree: "!" <expr>
    elif first_token == "!":
        expr_token = dana_expr.children[1]
        expr_type = get_expr_type(expr_token)
        if expr_type != DanaType("byte"):
            print("Lines {}: ".format(dana_expr.linespan), end="")
            print("Negation operator ! applied to nonbyte expression")
        return expr_type

    #Subtree: <int-const>
    elif first_token.name == "p_number":
        return DanaType("int")
    
    #Subtree: <char-const>
    elif first_token.name == "p_char":
        return DanaType("byte")

    #Subtree: "true" | "false"
    elif first_token.name == "p_boolean":
        return DanaType("byte")

    #Subtree: <lvalue>
    elif first_token.name == "p_lvalue":
        return get_lvalue_type(first_token) 

    #Subtree: <expr> ("+" | "-" | "*" | "/" | "%" ) <expr> | <expr> ("&" | "|") <expr>
    elif first_token.name == "p_expr":
        operation = dana_expr.children[1]
        op1 = dana_expr.children[0]
        op2 = dana_expr.children[2]            

        #Subtree: <expr> ("+" | "-" | "*" | "/" | "%" ) <expr> 
        if operation in ["+", "-", "STAR", "SLASH", "PERCENT"]:
            op1_type = get_expr_type(op1)
            op2_type = get_expr_type(op2)
            if op1_type != op2_type:
                print("Lines {}: ".format(dana_expr.linespan), end="")
                print("Type mismatch between expressions being compared. Types are {} and {}".format(op1_type, op2_type))
            elif op1_type not in [DanaType("int"), DanaType("byte")]:
                print("Lines {}: ".format(dana_expr.linespan), end="")
                print("Arithmetic operation between expressions of that are not of type int or byte")
        
            return op1_type

        #Subtree: <expr> ("&" | "|") <expr>
        elif operation in ["&", "|"]:
            op1_type = get_expr_type(op1)
            op2_type = get_expr_type(op2)
            if op1_type != DanaType("byte") or op1_type != DanaType("byte"):
                print("Lines {}: ".format(dana_expr.linespan), end="")
                print("Logical operation between expressions that are not of type byte")
        
            return DanaType("byte")

    #Subtree: <func-call>
    elif first_token.name == "p_func_call":
        function_name = first_token.children[0].value
        if not function_name in symbol_table:
            print("Lines {}: ".format(dana_expr.linespan), end="")
            print("Process {} not defined".format(function_name))

        call_ops = get_call_ops(dana_expr)

        if symbol_table[function_name].ops != call_ops:
            print("Lines {}: ".format(dana_expr.linespan), end="")
            print("Function {} not called with proper arguments".format(first_token.children[0].value))
        
        function_type = stack.name_type(function_name)
        return DanaType(function_type.base, dims = function_type.dims)


         

def verify_cond(dana_cond):
    first_token = dana_cond.children[0]

    #Subtree: "(" <cond> ")"
    if first_token == "(":
        cond_token = dana_cond.children[1]
        verify_cond(cond_token)

    #Subtree: "not" <cond>
    elif first_token == "not":
        cond_token = dana_cond.children[1]
        verify_cond(cond_token)


    #Subtree: <cond> ("and" | "or") <cond>
    elif first_token == "p_cond":
        op1 = dana_cond.children[0] 
        op2 = dana_cond.children[2] 
        verify_cond(op1)
        verify_cond(op2)

    #Subtree: <expr> | <expr> ("=" | "<>" | "<" | ">" | "<=" | ">=") <expr>
    elif first_token.name == "p_expr":
        #Subtree: <expr> 
        if len(dana_cond.children) == 1:
            expr_type = get_expr_type(first_token)
            if expr_type != DanaType("byte"):
                print("Lines {}: ".format(dana_cond.linespan), end="")
                print("Expression used as condition has type {}".format(expr_type))
        #Subtree: <expr> ("=" | "<>" | "<" | ">" | "<=" | ">=") <expr>
        else:
            op1 = dana_cond.children[0] 
            op2 = dana_cond.children[2] 
            op1_type = get_expr_type(op1)
            op2_type = get_expr_type(op2)
            if op1_type != op2_type:
                print("Lines {}: ".format(dana_cond.linespan), end="")
                print("Type mismatch between expressions being compared. Types are {} and {}".format(op1_type, op2_type))
            elif op1_type not in [DanaType("int"), DanaType("byte")]:
                print("Lines {}: ".format(dana_cond.linespan), end="")
                print("Comparison between expressions of a nonordered type")
                    


def verify_labeled_stmt(stmt, symbol_table):
    label = stmt.find_first("p_name")
    if label:
        label = label.value
        if label not in symbol_table:
            print("Lines {}: Label {} not defined in current scope".format(stmt.linespan, label))
        elif symbol_table[label] != DanaType("label"):
            print("Lines {}: Symbol {} not not a label".format(stmt.linespan, label))
    

def verify_call_stmt(stmt, symbol_table):
    # Get args, get symbol, compare 
    proc_name = stmt.find_first("p_name").value

    if proc_name not in symbol_table:
        print("Lines {}: Symbol {} not in scope".format(stmt.linespan, proc_name))
        
    exprs = stmt.find_all("p_expr")
    types = []
    for expr in exprs:
         types.append(get_expr_type(expr, symbol_table))

    expected_type = symbol_table[proc_name] if proc_name in symbol_table else DanaType("invalid")
    actual_type = DanaType("void", args = types)
    if expected_type != actual_type:
        print("Lines {}: Proc has type {} but called as {}".format(stmt.linespan, expected_type, actual_type))
        

def verify_ret_stmt(stmt, symbol_table):
    actual_type = symbol_table["$"]
    expr = stmt.find_first_child("p_expr")
    
    expected_type = get_expr_type(expr, symbol_table)
    if expected_type != actual_type:
        print("Lines {}: Function has type {} but returns {}".format(stmt.linespan, expected_type, actual_type))
    

def verify_assign_stmt(stmt, symbol_table):
    lvalue = stmt.get_first_child("p_lvalue")

    expected_type = None
    if lvalue.get_first_child("p_string"):
        expected_type = DanaType(byte, dims = [0])

    elif lvalue.get_first_child("p_name"):
        name = lvalue.get_first_child("p_name").value
        if name not in symbol_table:
            print("Lines {}: Symbol {} not in scope".format(stmt.linespan, name))
    else:
        expr = stmt.get_first_child("p_expr")
        if expr:
            expr_type = get_expr_type(expr,symbol_table) 
            if expr_type != DanaType("int"):
                print("Lines {}: Type {} used as index".format(stmt.linespan, expr_type))

        child_lvalue = lvalue.get_first_child("p_lvalue")
        child_type = get_lvalue_type(child_lvalue, symbol_table)
        if not child_type.dims:
            print("Lines {}: Base type {} dereferenced".format(stmt.linespan, child_type))
            expected_type = child_type
        else: 
            expected_type = DanaType(child_type.base, dims = child_type.dims[1:], args = child_type.ops)
    
    actual_type = get_expr_type(stmt.get_first_child("p_expr"), symbol_table)
    if expected_type != actual_type:
        print("Lines {}: Function has type {} but returns {}".format(stmt.linespan, expected_type, actual_type))
    
            


# Traverse statement block, checking its symbols against the current stack
def verify_block(block, symbol_table):
    if not block.stmts:
        for child in block.children:
            temp_table = copy(symbol_table) 
            if block.conds:
                for cond in block.conds:
                    verify_cond(cond, symbol_table)
            elif block.label:
                temp_table[block.label] = DanaType("label")
            
            verify_block(child, temp_table)
    else:
        for stmt in block.stmts:
            if stmt.multifind(["p_cont_stmt", "p_break_stmt"]):
                verify_labeled_stmt(stmt, symbol_table)
            elif stmt.find_first_child("p_proc_call"):
                verify_call_stmt(stmt, symbol_table)
            elif stmt.find_first_child("p_ret_stmt"):
                verify_ret_stmt(stmt, symbol_table)
            elif stmt.find_first_child("lvalue"):
                verify_assign_stmt(stmt, symbol_table)


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
        
    return


if __name__ == "__main__":
    test()
