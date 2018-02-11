from compiler.parser.lexer import lex, tokens
from compiler.parser.parser import parser

from ply.lex import LexError
from ply.yacc import YaccError 

import sys

if __name__ == "__main__":
    try:
        program = open(sys.argv[1], 'r')
        lexer = lex()
        yacc = parser(start='program')
        ast = yacc.parse(program.read(), tracking=True, debug=False)

        print(ast)
    except IOError:
        print("Unable to open file. Exiting...")
    except LexError:
        print("Lexing Error. Exiting...")
    except YaccError:
        print("Parsing Error. Exiting...")
