import sys
import ply.lex

separators = (
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'COMMA',
    'COLON',
    'ASSIGN',
    'NEWLINE',
)

elements = (
    'NAME',
    'NUMBER',
    'CHAR',
    'STRING',
)

operators = (
    'PLUS',
    'MINUS',
    'STAR',
    'SLASH',
    'PERCENT',
    'EXCLAMATION',
    'AMPERSAND',
    'VERTICAL',
    'EQUAL',
    'UNEQUAL',
    'LESS',
    'GREATER',
    'LESSEQUAL',
    'GREATEREQUAL',
)

reserved = {
    'and' : 'AND',
    'as' : 'AS',
    'begin' : 'BEGIN',
    'break' : 'BREAK',
    'byte' : 'BYTE',
    'continue' : 'CONTINUE',
    'decl' : 'DECL',
    'def' : 'DEF',
    'elif' : 'ELIF',
    'else' : 'ELSE',
    'end' : 'END',
    'exit' : 'EXIT',
    'false' : 'FALSE',
    'if' : 'IF',
    'is' : 'IS',
    'int' : 'INT',
    'loop' : 'LOOP',
    'not' : 'NOT',
    'or' : 'OR',
    'ref' : 'REF',
    'return' : 'RETURN',
    'skip' : 'SKIP',
    'true' : 'TRUE',
    'var' : 'VAR',
}

ignored = (
    'LINECOMMENT',
    'WHITESPACE',
    'COMMENT_START',
    'COMMENT_END',
)



t_PLUS = r'\+' 
t_MINUS = r'-' 
t_STAR = r'\*' 
t_SLASH = r'/' 
t_PERCENT = r'%'
t_EXCLAMATION = r'!'  
t_AMPERSAND = r'&'
t_VERTICAL = r'\|' 
t_EQUAL = r'=' 
t_UNEQUAL = r'<>' 
t_LESS = r'<' 
t_GREATER = r'>' 
t_LESSEQUAL = r'<='
t_GREATEREQUAL = r'>=' 
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_COMMA = r','
t_COLON = r':'
t_ASSIGN = r':='
t_ignore_WHITESPACE = r'\s'

####################################
#NOTE: Tabs are handled like spaces#
####################################

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return None 


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CHAR(t):
    r"\'(([^\\\'\"\n]?)|((\\[rtns0\\\'\"])|\\x[0-9a-f]{2,2}))\'"
    return t

def t_STRING(t):
    r'"((\\\")|(\')|[^"\n])*"'
    return t

def t_NAME(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_ignore_LINECOMMENT(t):
    r'\#([^\n])*\n'

states = (
    ('comment', 'exclusive'),
)

def t_COMMENT_START(t):
    r'\(\*'
    t.lexer.push_state('comment')	

t_comment_COMMENT_START = t_COMMENT_START
	
def t_comment_COMMENT_END(t):
    r'\*\)'
    t.lexer.pop_state()	

# Not ACTUALLY an error state; rather, 
# it catches everything in the comments 
def t_comment_error(t):
    t.lexer.skip(1)

def t_error(t):
    print("Tokenization error. Offending character:\t %s" % t.value[0])
    print("Warning: Parsing might be _fantastically_ broken from here")
    t.lexer.skip(1)

tokens =  separators + elements + operators \
            + tuple(reserved.values())  + ignored


def test():
    if len(sys.argv) < 2:
        print("No input given")
        return;

    lexer = lex()
    try:
        program = open(sys.argv[1], 'r')
    except:
        print("Unable to open file. Exiting...")
        return
    lexer.input(program.read())

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

    return

def lex():
    return ply.lex.lex()

if __name__ == "__main__" :

    test()

