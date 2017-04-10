import sys
from lexer import lex as lex 
from lexer import tokens
from ply.yacc import yacc as yacc

precedence = (
    ('left', 'PLUS', 'MINUS', 'VERTICAL'),
    ('left', 'STAR', 'SLASH', 'PERCENT', 'AMPERSAND'),
    ('right', 'UPLUS', 'UMINUS', 'EXCLAMATION'), 
    ('nonassoc', 'EQUAL', 'UNEQUAL', \
        'LESS', 'GREATER', 'LESSEQUAL', 'GREATEREQUAL'),
    ('right', 'NOT'),
    ('left', 'AND'),
    ('right', 'OR'), 
)

# In order to convert the extended BNF grammar given to regular BNF,
# intermediate tokens are created. These are noted with comments




def p_data_type(p):
    '''
        data_type : INT
                  | BYTE
    '''
def p_type(p):
    '''
        type : data_type 
             | data_type index_list
    '''

# Helper token
def p_index_list(p):
    '''
        index_list : index_list LBRACK NUMBER RBRACK
                   | LBRACK NUMBER RBRACK 
    '''

def p_var_def(p):
    '''
        var_def : VAR NAME_list IS type 
    '''
# Helper token
def p_NAME_list(p):
    '''
        NAME_list : NAME_list NAME
                  | NAME
    '''

def p_stmt(p):
    '''
        stmt : SKIP
             | lvalue ASSIGN expr
             | proc_call
             | EXIT
             | RETURN COLON expr
             | IF cond COLON block 
             | IF cond COLON block ELSE COLON block 
             | IF cond COLON block elif_chain 
             | IF cond COLON block elif_chain ELSE COLON block 
             | LOOP COLON block
             | LOOP NAME COLON block
             | BREAK
             | BREAK COLON NAME
             | CONTINUE
             | CONTINUE COLON NAME
    '''

#Helper token
def p_elif_chain(p):
    '''
       elif_chain : elif_chain ELIF cond COLON block 
                  | ELIF cond COLON block 
    '''

def p_block(p):
    '''
        block : BEGIN stmt_list END
    '''


#Helper token
def p_stmt_list(p):
    '''
       stmt_list : stmt_list stmt 
                 | stmt 
    '''

def p_proc_call(p):
    '''
        proc_call : NAME 
                  | NAME COLON expr_list 
    '''

def p_func_call(p):
    '''
        func_call : NAME LPAREN RPAREN
                  | NAME LPAREN expr_list RPAREN
    '''

# Helper token
def p_expr_list(p):
    '''
        expr_list : expr_list COMMA expr 
                  | expr 
    '''

def p_lvalue(p):
    '''
        lvalue : NAME 
               | STRING 
               | lvalue LBRACK expr RBRACK
    '''

def p_expr(p):
    '''
        expr : NUMBER 
             | CHAR 
             | lvalue
             | LPAREN expr RPAREN
             | func_call
             | PLUS expr %prec UPLUS
             | MINUS expr %prec UMINUS
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
    print("Parsing error on token", p)
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
