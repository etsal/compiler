import sys
from functools import wraps
from ply.yacc import yacc as yacc
from frontend.lexer import lex as lex, tokens as tokens
from helper.tree import Node as Node  

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

# Decorator for building the AST
def ast_node():
    def decorate(func):
        # Needed to preserve the original function's name
        @wraps(func)
        def wrapper(p):
            func(p)
            p[0] = Node(func.__name__, *p[1:])            
        # Line number update needed for the parser
        wrapper.co_firstlineno = func.__code__.co_firstlineno
        return wrapper
    return decorate

def ast_value(dana_type = None):
    def decorate(func):
        # Needed to preserve the original function's name
        @wraps(func)
        def wrapper(p):
            func(p)
            p[0] = Node(func.__name__, value = p[1])            
        # Line number update needed for the parser
        wrapper.co_firstlineno = func.__code__.co_firstlineno
        return wrapper
    return decorate

# In order to convert the extended BNF grammar given to regular BNF,
# intermediate tokens are created. These are noted with comments
@ast_node()
def p_program(p):
    '''
        program : func_def
    '''

@ast_node()
def p_func_def(p):
    '''
        func_def : DEF header block
                 | DEF header local_def_list block
    '''

# Helper token
@ast_node()
def p_local_def_list(p):
    '''
        local_def_list : local_def_list local_def 
                       | local_def 
    '''

@ast_node()
def p_header(p):
    '''
        header : name maybe_data_type maybe_parameter_list
    '''

# Helper token
@ast_node()
def p_maybe_data_type(p):
    '''
        maybe_data_type : IS data_type
                        |
    '''

# Helper token
@ast_node()
def p_maybe_parameter_list(p):
    '''
        maybe_parameter_list : COLON fpar_def 
                             | COLON fpar_def parameter_list
                             |
    '''

# Helper token
@ast_node()
def p_parameter_list(p):
    '''
        parameter_list : parameter_list COMMA fpar_def
                       | COMMA fpar_def
    '''

@ast_node()
def p_fpar_def(p):
    '''
        fpar_def : name_list AS fpar_type
    '''

# Helper token
@ast_node()
def p_name_list(p):
    '''
        name_list : name_list name 
                  | name
    '''

@ast_value()
def p_data_type(p):
    '''
        data_type : INT
                  | BYTE
    '''

@ast_node()
def p_type(p):
    '''
        type : data_type 
             | data_type index_list
    '''

@ast_node()
def p_fpar_type(p):
    '''
        fpar_type : type 
                  | ref data_type
                  | data_type empty_brackets 
                  | data_type empty_brackets index_list 
    '''

# Helper token
@ast_node()
def p_index_list(p):
    '''
        index_list : index_list LBRACK number RBRACK
                   | LBRACK number RBRACK 
    '''

@ast_node()
def p_local_def(p):
    '''
        local_def : func_def
                  | func_decl
                  | var_def
    '''

@ast_node()
def p_func_decl(p):
    '''
        func_decl : DECL header 
    '''

@ast_node()
def p_var_def(p):
    '''
        var_def : VAR name_list IS type 
    '''

@ast_node()
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
             | LOOP name COLON block
             | BREAK
             | BREAK COLON name
             | CONTINUE
             | CONTINUE COLON name
    '''

# Helper token
@ast_node()
def p_elif_chain(p):
    '''
       elif_chain : elif_chain ELIF cond COLON block 
                  | ELIF cond COLON block 
    '''

@ast_node()
def p_block(p):
    '''
        block : BEGIN stmt_list END
    '''


# Helper token
@ast_node()
def p_stmt_list(p):
    '''
       stmt_list : stmt_list stmt 
                 | stmt 
    '''

@ast_node()
def p_proc_call(p):
    '''
        proc_call : name 
                  | name COLON expr_list 
    '''

@ast_node()
def p_func_call(p):
    '''
        func_call : name LPAREN RPAREN
                  | name LPAREN expr_list RPAREN
    '''

# Helper token
@ast_node()
def p_expr_list(p):
    '''
        expr_list : expr_list COMMA expr 
                  | expr 
    '''

@ast_node()
def p_lvalue(p):
    '''
        lvalue : name 
               | lvalue LBRACK expr RBRACK
    '''

@ast_node()
def p_expr(p):
    '''
        expr : number 
             | char 
             | string 
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
             | boolean 
             | EXCLAMATION expr
             | expr AMPERSAND expr
             | expr VERTICAL expr 

    '''

# Helper token
@ast_node()
def p_xcond(p):
    '''
        xcond : LPAREN xcond RPAREN
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

@ast_node()
def p_cond(p):
    '''
        cond : expr
             | xcond
    '''

# Helper tokens from here on downwards
# Used to build the AST more easily


@ast_node()
def p_ref(p):
   '''
        ref : REF 
   ''' 
        
@ast_node()
def p_empty_brackets(p):
   '''
        empty_brackets : LBRACK RBRACK 
   ''' 
    

@ast_value()
def p_name(p):
   '''
        name : NAME
   ''' 

@ast_value()
def p_char(p): 
   '''
        char : CHAR 
   ''' 

@ast_value()
def p_number(p):
   '''
        number : NUMBER 
   ''' 
    
@ast_value()
def p_boolean(p):
   '''
        boolean : TRUE
                | FALSE
   ''' 
    
@ast_value()
def p_string(p):
   '''
        string : STRING 
   ''' 
 
def p_error(p):
    print("Parsing error on token", p)
    return;

def parser(start):
    return yacc(start=start, write_tables=False)

def test():
    lexer = lex() 
    try:
        program = open(sys.argv[1], 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        return

#    lexer.input(program.read())
    
    parser = yacc(start='program', write_tables=False)

    ast = parser.parse(program.read(),debug=False)
    print(ast)
    #print("TOP: " + ast.top().name)

    return
    

if __name__ == "__main__":
    test()
