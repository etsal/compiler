import sys
from ply.lex import lex as lex

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
    'FULLCOMMENT',
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

##########################################
#TODO: Reset column each time line changes
##########################################
def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	return t

t_ignore_WHITESPACE = r'\s'

#########################################
#TODO: Add comment handling
#########################################

def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t

def t_CHAR(t):
	r"\'(([^\\\'\"\n]?)|((\\[ts0\\\'\"])|\\x[0-9a-f]{2,2}))\'"
	return t

#################THIS IS WRONG NEEDS TO CHANGE#####################
def t_STRING(t):
	r'"(?:\\.|[^"\\])*"'
	return t
##################################################################

def t_NAME(t):
	r'[a-zA-Z_][a-zA-Z_0-9]*'
	return t

def t_error(t):
    print("Illegal character detected:\t %s" % t.value[0])
    t.lexer.skip(1)

tokens =  separators + elements + operators \
            + tuple(reserved.values())  + ignored


def test():
    if len(sys.argv) < 2:
        print("No input given")
        return;

    lexer = lex()

    program = open(sys.argv[1], 'r')
    lexer.input(program.read())

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

    return


if __name__ == "__main__" :

    test()

