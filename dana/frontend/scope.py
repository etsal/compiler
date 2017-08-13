import sys
from collections import deque as deque
from frontend.lexer import lex as lex, tokens as tokens
from frontend.parser import parser as parser
from helper.tree import Node as Node  


# The stack used to check scoping and typing rules
class ScopeStack(object):

    # The full list of builtin functions
    builtins = [
        "writeInteger", "writeByte", "writeChar", "writeString", \
        "readInteger", "readByte", "readChar", "readString",     \
        "strlen", "strcmp", "strcat", "strcpy",                  \
        "extend", "shrink"                                       \
    ]

    def __init__(self, ast):

        self.ast = ast
        self.stack = deque() 

        # Push the builtins into the stack
        self.add_scope()
        for builtin in self.builtins:
            self.push_symbol(builtin)
        
    def traverse_function(self, dana_function):

        # The function is valid only for ASTs with p_func_def as the root token
        if dana_function.name != "p_func_def":
            raise ValueError

        self.add_scope()

        symbols = deque()
        dana_block = None

        unprocessed = deque([dana_function])
        while len(unprocessed) > 0:
            child = unprocessed.pop()
            # Try/Catch in case the child is a string
            # (that is, the token is a terminal one)
            try:
                if child.name == "p_func_decl":                     
                    # Get into the header nonterminal, grab the id terminal
                    cur_symbol = child.children[1].children[0].value
                    if cur_symbol in self.stack[0]:
                        print("Symbol {} already defined in current scope!".format(cur_symbol))
                        return
                    self.push_symbol(cur_symbol)
                    continue

                elif child.name == "p_func_def" and child != dana_function:
                    cur_symbol = child.children[1].children[0].value
                    if cur_symbol in self.stack[0]:
                        print("Symbol {} already defined in current scope!".format(cur_symbol))
                        return
                    self.push_symbol(cur_symbol)
                    self.traverse_function(child)
                    continue

                elif child.name == "p_name_list":
                    cur_symbols = [var.value for var in child.children if var.name == "p_name"]    
                    for cur_symbol in cur_symbols:
                        if cur_symbol in self.stack[0]:
                            print("Symbol {} already defined in current scope!".format(cur_symbol))
                    self.push_symbols(cur_symbols)    

                # Once we reach the block, we cannot find any more definitions
                elif child.name == "p_block":
                    dana_block = child
                    break

                # Appending done this way to DFS the AST - if done otherwise, 
                # the AST would not be traversed correctly
                new_unprocessed =  child.children.__copy__()
                new_unprocessed.reverse()
                unprocessed.extend(new_unprocessed)

            except AttributeError:
                continue


        self.print_scopes()

        # Now the only thing we may find is names being used - no new declarations
        # So we check each one against the current scope stack
        unprocessed = deque([dana_block])
        while len(unprocessed) > 0:
            child = unprocessed.popleft()
            try:
                if child.name == "p_name":
                    if all(child.value not in scope for scope in self.stack):
                        print("Symbol not found! Offending value:\t" + child.value)
                        return 
                unprocessed.extend(child.children)
            except AttributeError:
                continue

        print("Scoping rules adhered to.")
        self.pop_scope()


    def add_scope(self):
        self.stack.appendleft(deque())

    def pop_scope(self):
        return self.stack.popleft()


    def push_symbol(self, symbol):
        self.stack[0].append(symbol)

    def push_symbols(self, symbols):
        self.stack[0].extend(symbols)
    

    def print_scopes(self):
        for scope in self.stack:
            print(scope)

    def print_top_scope(self):
        print(self.stack[0])


def test():
    try:
        program = open(sys.argv[1], 'r')
    except IOError:
        print("Unable to open file. Exiting...")
        return
    lexer = lex()  
    yacc = parser(start='program')
    ast = yacc.parse(program.read(),debug=False)
    try:
        scope = ScopeStack(ast)
        scope.traverse_function(ast.children[0])
        
    except ValueError:
        print("Exception: argument to _func_defs not a program")
        

    return
    

if __name__ == "__main__":
    test()
