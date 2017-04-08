import sys
from lexer import lex as lex 
from lexer import tokens
from ply.yacc import yacc as yacc

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'SLASH'),
    
)

def p_lvalue(p):
    '''
        lvalue : NAME 
               | STRING 
               | lvalue LBRACK expr RBRACK
    '''
#NOTE: Insert "| func_call" to the rule below once it is defined

def p_expr(p):
    '''
        expr : NUMBER 
             | CHAR 
             | lvalue
             | LPAREN expr RPAREN
             | PLUS expr
             | MINUS expr
             | expr PLUS expr
             | expr MINUS expr
             | expr STAR expr
             | expr SLASH expr
             | expr PERCENT expr
             | TRUE
             | FALSE
             | EXCLAMATION expr
             | expr AMPERSAND expr
             | expr VERTICAL expr 

    '''

def p_cond(p):
    '''
        cond : expr 
             | LPAREN cond RPAREN 
             | NOT cond
             | cond AND cond
             | cond OR cond
             | expr EQUAL expr
             | expr UNEQUAL expr
             | expr LESS expr
             | expr GREATER expr
             | expr LESSEQUAL expr 
             | expr GREATEREQUAL expr 
    '''

def p_error(p):
    print("Parsing error on token {}", p)
    return;

def test():
    lexer = lex() 
    try:
        program = open(sys.argv[1], 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        return

#    lexer.input(program.read())
    
    parser = yacc(start='expr')

    parser.parse(program.read(),debug=False)

    return
    

if __name__ == "__main__":
    test()
