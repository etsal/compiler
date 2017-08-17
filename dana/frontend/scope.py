import sys
from collections import deque as deque
from frontend.lexer import lex as lex, tokens as tokens
from frontend.parser import parser as parser
from helper.tree import Node as Node  
from helper.type import DanaType as DanaType 
from helper.scope_stack import ScopeStack as ScopeStack



# The stack used to check scoping and typing rules
class SemanticsChecker(object):
    # The full list of builtin functions
    builtins = [
        ("writeInteger", DanaType("void", ops = [DanaType("int")])), 
        ("writeByte", DanaType("void", ops = [DanaType("byte")])), 
        ("writeChar", DanaType("void", ops = [DanaType("byte")])),
        ("writeString", DanaType("void", ops = [DanaType("byte", [0])])), 
        ("readInteger", DanaType("int", ops = [DanaType("void")])), 
        ("readByte", DanaType("byte", ops = [DanaType("void")])), 
        ("readChar", DanaType("byte", ops = [DanaType("void")])), 
        ("readString", DanaType("byte", [0], ops = [DanaType("void")])),     
        ("strlen", DanaType("int", ops = [DanaType("byte", [0])])), 
        ("strcmp", DanaType("int", ops = [DanaType("byte", [0]), DanaType("byte", [0])])), 
        ("strcat", DanaType("byte", [0], ops = [DanaType("byte", [0]), DanaType("byte", [0])])), 
        ("strcpy", DanaType("byte", [0], ops = [DanaType("byte", [0]), DanaType("byte", [0])])), 
        ("extend", DanaType("int", ops = [DanaType("byte")])), 
        ("shrink", DanaType( "byte", ops = [DanaType("int")])), 
        ("main", DanaType("void", ops = [DanaType("void")])),
    ]

    def __init__(self, ast):

        self.ast = ast
        self.scope_stack = ScopeStack() 
        
        # Push the builtins into the stack in their own scope
        self.scope_stack.add_scope()
        self.scope_stack.push_symbols(self.builtins)
        

    # Helper method used when traversing the AST
    @staticmethod
    def extendleft_no_reverse(main_deque, new_elems):
        new_elems_copy = new_elems.__copy__()
        new_elems_copy.reverse()
        main_deque.extendleft(new_elems_copy) 

    def traverse_type(self, dana_type):
        total_type = DanaType("void")
        
        unprocessed = deque(dana_type.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_data_type":
                    total_type.base = self.traverse_data_type(child)
                elif child.name == "number":
                    total_type.reflevel += child.value  
                else:
                   self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue
        return total_type
        

    def traverse_fpar_type(self, dana_fpar_type):
        total_type = DanaType("void")
        unprocessed = deque(dana_fpar_type.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_ref":
                    total_type.ref = True

                elif child.name == "p_data_type":
                    total_type.base = self.traverse_data_type(child)

                elif child.name == "p_type":
                    total_type = self.traverse_type(child)

                elif child.name == "p_empty_brackets":                
                     total_type.dimensions += [0]
            
                elif child.name == "p_number":
                     total_type.dimensions += [number]
         
                else:
                   self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue
        return total_type

    # Traverses both p_var_def and p_fpar_def tokens
    def traverse_def(self, dana_def):
        symbols = deque() 
        symbol_type = None
        unprocessed = deque(dana_def.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_name":
                   symbols.append(child.value)

                elif child.name == "p_type":
                   symbol_type = self.traverse_type(child) 

                elif child.name == "p_fpar_type":
                   symbol_type = self.traverse_fpar_type(child)

                else:
                   self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue
                

        return [(symbol, symbol_type) for symbol in symbols]
    

    def traverse_data_type(self, dana_data_type):
        if dana_data_type.value == "INT":
            return "int"

        elif dana_data_type.value == "BYTE":
            return "byte"


    # Traverse function header, extracting the type of the function it refers to
    def traverse_header(self, dana_header):        
        function_name = None
        function_type = "void"
        argument_types = []

        unprocessed = deque(dana_header.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                
                if child.name == "p_name":
                    function_name = child.value

                elif child.name == "p_data_type":
                    function_type = traverse_data_type(child)

                # We just get the type of the parameter
                elif child.name == "p_fpar_def":
                    argument_types += [y for (x,y) in self.traverse_def(child)] 

                else:
                    self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue

        return (function_name, DanaType(function_type, ops = argument_types))

            
    

    # TODO: Exit more abruptly on error (with an appropriate exception probably)
    def traverse_function(self, dana_function):

        dana_block = None
        unprocessed = deque(dana_function.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:

                if child.name == "p_func_decl" or child.name == "p_func_def":                     
                    
                    func_symbol = self.traverse_header(child.children[1])                                         

                    if self.scope_stack.in_current_scope(func_symbol):
                        print("Symbol {} already defined in current scope!".format(func_symbol))
        
                    self.scope_stack.push_symbol(func_symbol)

                    # If child is a full function definition, check its semantics, too
                    if child.name == "p_func_def":
                        self.scope_stack.add_scope()
                        self.traverse_function(child)
                        self.scope_stack.pop_scope()

                # If we just find a p_fpar_def token, that means that it's a parameter of the 
                # function being traversed. Likewise, if we find a p_var_def token, it's a 
                # local definition

                elif child.name == "p_var_def" or child.name == "p_fpar_def":
                    new_symbols = self.traverse_def(child)

                    for new_symbol in new_symbols:
                        if self.scope_stack.in_current_scope(new_symbol):
                            print("Symbol {} already defined in current scope!".format(new_symbol))
                        
                        
                    self.scope_stack.push_symbols(new_symbols)
                    

                # Once we reach the block, we cannot find any more definitions
                elif child.name == "p_block":
                    dana_block = child
                    break

                else:
                    self.extendleft_no_reverse(unprocessed, child.children)
                    

            # Try/Catch in case the child is a string
            # (that is, the token is a terminal one)
            except AttributeError:
                continue

        self.scope_stack.print_top_scope()
        
        # self.traverse_block(dana_block)


    # TODO: Recursively determine the type of each expression, attach it to it
    # Traverse statement block, checking its symbols against the current stack
    def traverse_block(self, dana_block):


        # Now the only thing we may find is names being used - no new declarations
        # So we check each one against the current scope stack
        unprocessed = deque([dana_block])
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_name":
                    if all((child.value, DanaType("void", 0)) not in scope for scope in self.scope_stack.stack):
                        print("Symbol not found! Offending value:\t" + child.value)
                self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue

        
    def check(self):
        self.scope_stack.add_scope()
        self.traverse_function(self.ast.children[0]) 
        self.scope_stack.pop_scope()
        

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
        scope = SemanticsChecker(ast)
        scope.check()
        
    except ValueError as e:
        print("Exception: {}".format(str(e)))
        

    return
    

if __name__ == "__main__":
    test()
