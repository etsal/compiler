import sys
from copy import copy
from collections import deque as deque
from compiler.parser.lexer import lex as lex, tokens as tokens
from compiler.parser.parser import parser as parser
from compiler.semantic.symbol import Symbol as Symbol 
from compiler.semantic.type import DanaType as DanaType 
from compiler.semantic.expr import DanaExpr as DanaExpr 


def verify_labeled_stmt(stmt, symbol_table):
    label = stmt.find_first("p_name")
    if label:
        label = label.value
        if label not in symbol_table:
            print("Lines {}: Label {} not defined in current scope".format(stmt.linespan, label))
        elif symbol_table[label] != DanaType("label"):
            print("Lines {}: Symbol {} not not a label".format(stmt.linespan, label))
    

def verify_call_stmt(stmt, symbol_table):
    proc_name = stmt.find_first("p_name").value
    if proc_name not in symbol_table:
        print("Lines {}: Symbol {} not in scope".format(stmt.linespan, proc_name))
        return 
        
    types = []
    exprs = stmt.find_all("p_expr")
    for expr in exprs:
         types.append(DanaExpr(expr, symbol_table).type)

    expected_type = symbol_table[proc_name] if proc_name in symbol_table else DanaType("invalid")
    actual_type = DanaType("void", args = types)
    if expected_type != actual_type:
        print("Lines {}: Proc has type {} but called as {}".format(stmt.linespan, str(expected_type), str(actual_type)))
        

def verify_ret_stmt(stmt, symbol_table):    
    expected_type = DanaType(symbol_table["$"].base)
    actual_type = DanaType("void")

    expr = stmt.find_first("p_expr")
    if expr:
        actual_type = DanaExpr(expr, symbol_table).type

    if expected_type != actual_type:
        print("Lines {}: Function has type {} but returns {}".format(stmt.linespan, expected_type, actual_type))
    

def verify_assign_stmt(stmt, symbol_table):
    expected_type = DanaExpr(stmt.get_first_child("p_lvalue"), symbol_table).type 
    actual_type = DanaExpr(stmt.get_first_child("p_expr"), symbol_table).type
    if expected_type != actual_type:
        print("Lines {}: Function has type {} but returns {}".format(stmt.linespan, expected_type, actual_type))
    
            


# Traverse statement block, checking its symbols against the current stack
def verify_block(block, symbol_table):
    if not block.stmts:
        temp_table = copy(symbol_table) 
        if block.conds:
            conds = [DanaExpr(cond, symbol_table) for cond in block.conds]
            block.conds=  conds
        if block.label:
            temp_table[block.label] = DanaType("label")
            
        for child in block.children:
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
