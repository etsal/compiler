from compiler.parser.lexer import lex 
from compiler.parser.tokrules import tokens
from compiler.parser.parser import parser
from compiler.semantic.semantic import produce_program
from compiler.codegen.codegen import irgen 

from ply.lex import LexError
from ply.yacc import YaccError 
from compiler.semantic.table import Table 
from compiler.semantic.type import DanaType

import sys

if __name__ == "__main__":
    try:
        program = open(sys.argv[1], 'r')
        lexer = lex()
        yacc = parser(start='program')
        ast = yacc.parse(program.read(), tracking=True, debug=False, lexer=lexer)

        main_function = ast.children[0]
        function = produce_program(main_function)
        print(function)
    except IOError:
        print("Unable to open file. Exiting...")
    except LexError:
        print("Lexing Error. Exiting...")
    except YaccError:
        print("Parsing Error. Exiting...")
    except Table.ScopeError:
        print("Scope Error. Exiting...")
    except DanaType.DanaTypeError:
        print("DanaType Error. Exiting...")
        
