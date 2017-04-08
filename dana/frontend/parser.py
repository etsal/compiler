import sys
from lexer import lex as lex 
from ply.yacc import yacc as yacc

def test():
    lexer = lex() 

    program = open(sys.argv[1], 'r')
    lexer.input(program.read())

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

    return
    

if __name__ == "__main__":
    test()	
