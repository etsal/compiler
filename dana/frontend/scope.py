import sys
from functools import wraps
from frontend.lexer import lex as lex, tokens as tokens
from frontend.parser import parser as parser
from helper.tree import Node as Node  


def test():
    lexer = lex() 
    try:
        program = open(sys.argv[1], 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        return

#    lexer.input(program.read())
    
    yacc = parser(start='program')

    ast = yacc.parse(program.read(),debug=False)
    print(ast)
    #print("TOP: " + ast.top().name)

    return
    

if __name__ == "__main__":
    test()
