from compiler.parser.lexer import lex, tokens
from compiler.parser.parser import parser
from compiler.semantic.semantic import produce_program
from compiler.codegen.codegen import irgen 

from ply.lex import LexError
from ply.yacc import YaccError 
from compiler.semantic.table import Table 
from compiler.semantic.type import DanaType
from compiler.builtinIR import BUILTINS_IR

import os
import sys
import argparse
from subprocess import call


def get_args():
    argparser = argparse.ArgumentParser(description="Dana compiler.")
    group = argparser.add_mutually_exclusive_group()
    group.add_argument("-f", action="store_true", help="Take program from stdin, print .asm to stdout")
    group.add_argument("-i", action="store_true", help="Take program from stdin, print .imm to stdout")
    group.add_argument("filepath", nargs="?", help="Source filepath")
    return argparser.parse_args()


def path_parts(args):
    """
        Get the directory of the source file, as well
        as the desired name of the output files.
    """
    if not args.filepath:
        return ("", ".tmp")

    path, name = os.path.split(args.filepath)

    if not name or '.' not in name:
        print("Invalid file name. Exiting...")
        sys.exit(1)
    prefix, _ = os.path.splitext(name)

    return (path, prefix)

def get_program(args):
    try:
        return sys.stdin if (args.f or args.i) else open(args.filepath, 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        sys.exit(1)


def get_module(program):
    """"
        Get the LLVM IR module for the input program
    """
    try:
        lexer = lex()
        yacc = parser(start='program')
        ast = yacc.parse(program.read(), tracking=True, debug=False)

        main_function = ast.children[0]
        function = produce_program(main_function)
        module = irgen(function)

        return module
    except LexError:
        print("Lexing Error. Exiting...")
        sys.exit(1)
    except YaccError:
        print("Parsing Error. Exiting...")
        sys.exit(1)
    except Table.ScopeError:
        print("Scope Error. Exiting...")
        sys.exit(1)
    except DanaType.DanaTypeError:
        print("DanaType Error. Exiting...")
        sys.exit(1)

    # Unreachable
    return None


if __name__ == "__main__":

    args = get_args()    
    path, prefix = path_parts(args)

    program =  get_program(args)
    module = get_module(program) 

    # If -i is set, redirect to stdout and do not generate assembly
    if args.i:
        print(module)
        sys.exit(0)
    
    irfilename = os.path.join(path, prefix + ".imm")
    with open(irfilename, "w+") as irfile:
        irfile.write(str(module))
         
    # If -f is set, redirect to stdout and do not generate executable
    if args.f:
        call(["llc", irfilename , "-o", "/dev/stdout"])  
        # We do not need the ir if we have the -f option
        os.remove(irfilename) 
        sys.exit(0)


    # In order to package the library with the compiler, we use
    # a hack where we hold the builtin IR code in Python, and
    # write it to a file at the target directory
    builtinsirname = os.path.join(path, ".builtins.imm")
    builtinsasmname = os.path.join(path, ".builtins.asm")
    with open(builtinsirname, "w+") as builtins:
        builtins.write(BUILTINS_IR)
        


    asmfilename = os.path.join(path, prefix + ".asm")
    execname = os.path.join(path, prefix)
    call(["llc", "-relocation-model=pic", irfilename, "-o", asmfilename]) 
    call(["llc", "-relocation-model=pic", builtinsirname, "-o", builtinsasmname]) 
    call(["clang", "-fPIC", asmfilename, builtinsasmname, "-o", execname]) 

    # Remove the builtin IR/Assembly code
    os.remove(builtinsirname)
    os.remove(builtinsasmname)

    sys.exit(0)
