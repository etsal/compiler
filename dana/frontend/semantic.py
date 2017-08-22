import sys
from collections import deque as deque
from copy import deepcopy as deepcopy
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

    def get_total_data_type(self, dana_type):
        total_type = DanaType("void")
        
        unprocessed = deque(dana_type.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_data_type":
                    total_type.base = self.get_primitive_data_type(child)
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
                    total_type.base = self.get_primitive_data_type(child)

                elif child.name == "p_type":
                    total_type = self.get_total_data_type(child)

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
    def get_variable_symbols(self, dana_def):
        symbols = deque() 
        symbol_type = None
        unprocessed = deque(dana_def.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_name":
                   symbols.append(child.value)

                elif child.name == "p_type":
                   symbol_type = self.get_total_data_type(child) 

                elif child.name == "p_fpar_type":
                   symbol_type = self.traverse_fpar_type(child)

                else:
                   self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue
                

        return [(symbol, symbol_type) for symbol in symbols]
    

    def get_primitive_data_type(self, dana_data_type):
        if dana_data_type.value == "INT":
            return "int"

        elif dana_data_type.value == "BYTE":
            return "byte"


    # Traverse function header, extracting the type of the function it refers to
    def get_function_type(self, dana_header):        
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
                    function_type = get_primitive_data_type(child)

                # We just get the type of the parameter
                elif child.name == "p_fpar_def":
                    argument_types += [y for (x,y) in self.get_variable_symbols(child)] 

                else:
                    self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue

        return (function_name, DanaType(function_type, ops = argument_types))

            
    

    # TODO: Exit more abruptly on error (with an appropriate exception probably)
    def get_function_scope(self, dana_function):

        current_function = self.get_function_type(dana_function.children[1])
        self.scope_stack.add_scope(current_function)

        dana_block = None
        unprocessed = deque(dana_function.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:

                if child.name == "p_func_decl" or child.name == "p_func_def":                     
                    
                    func_symbol = self.get_function_type(child.children[1])                                         

                    if self.scope_stack.in_current_scope(func_symbol):
                        print("Symbol {} already defined in current scope!".format(func_symbol))
        
                    self.scope_stack.push_symbol(func_symbol)

                    # If child is a full function definition, check its semantics, too
                    if child.name == "p_func_def":
                        self.get_function_scope(child)

                # If we just find a p_fpar_def token, that means that it's a parameter of the 
                # function being traversed. Likewise, if we find a p_var_def token, it's a 
                # local definition

                elif child.name == "p_var_def" or child.name == "p_fpar_def":
                    new_symbols = self.get_variable_symbols(child)

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

        self.scope_stack.pop_scope()


    ########################################################################################
    ########################################################################################
    ########################################################################################

    def traverse_statement(self, dana_statement):
        first_token = dana_statement.children[0]


        if first_token == "SKIP":
            pass 


        elif first_token == "RETURN" or first_token == "EXIT":
            if first_token == "RETURN":
                return_expression = dana_statement.children[2]
                return_type = self.traverse_expression(return_expression)
            else:
                return_type = DanaType("void")

            current_function = self.stack.top_function()
            if return_type != current_function[1]:
                print("Type mismatch: Function {} returns {}, but return expression is of type {}"
                            .format(current_function[0], current_function[1], return_type))
            

        elif first_token == "IF":
            traverse_if_statement(dana_statement)


        elif first_token == "LOOP":
            # If there is a label, store it
            if len(dana_statement.children) == 4:
                this.stack.push_symbol((dana_statement.children[1].value, DanaType("label")))

            looped_block = dana_statement.children[-1]
            traverse_block(looped_block)


        # These two are handled identically at a semantic level
        elif first_token == "BREAK" or first_token == "CONTINUE":
            if len(dana_statement.children) > 1:
                label_name = dana_statement.children[2].value
                if not self.scope.in_stack(label_name):
                    print("Label not found: {}".format(label_name))
                symbol_type = self.scope_stack.first_type(label_name)

                if symbol_type is None:
                    print("Label named {} not found!".format(label_name))
                    return

                if symbol_type != DanaType("label"):
                    print("Nonlabel id {} used as label".format(label_name))
                        

        elif first_token.name == "p_lvalue":
           lvalue_type = self.traverse_lvalue(dana_statement.children[0]) 
           expr_type = self.traverse_expr(dana_statement.children[2]) 

           if lvalue_type != expr_type:
                print("Lvalue is of type {}, but is assigned an expression of type {}".format(lvalue_type, expr_type))


        # Procs are have return type void by design, so no need to check that
        elif first_token.name == "p_proc_call":
            process_name = first_token.children[0]
            if not self.scope_stack.in_stack(process_name):
                print("Process {} not defined".format(process_name))
            definition_type = self.stack.first_type(dana_statement.children[0].value) 
            call_ops = traverse_call(dana_statement)

            if definition_type != DanaType("void", ops = call_ops):
                print("Problem by process call {}".format(first_token.children[0].value))

                 
    def traverse_lvalue(self, dana_lvalue):
        first_token = dana_lvalue.children[1]
        if first_token.name == name:
            if not self.scope_stack.in_stack(first_token.value):
                print("Symbol {} not defined!".format(name))
          
            return copy.deepcopy(self.scope_stack.first_type(name)) 
        else:
            
            base_type = self.traverse_lvalue(first_token) 
            expr_type = self.traverse_expr(dana_lvalue.children[3])
            if expr_type != DanaType("int"):
                print("Expression used as index is of type {}".format(expr_type))
            if not base_type.dimensions:
                print("Nonarray lvalue dereferenced") 
            base_type.dimensions = base_type.dimensions[:-1]
            return base_type
             

    def traverse_call(self, dana_call):
        call_ops = []
        unprocessed = deque(dana_call.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_expr":
                    call_ops += self.traverse_expr(child)

                else:
                    self.extendleft_no_reverse(unprocessed, child.children) 
        
            except AttributeError:
                continue
        
        return call_ops


    def traverse_cond(self, dana_cond):
        first_token = dana_cond.children[0]
        if first_token == "(":
            self.traverse_cond(dana_cond.children[2])


        elif first_token == "NOT":
            self.traverse_cond(dana_cond.chilren[1])


        elif first_token == "p_cond":
            self.traverse_cond(dana_cond.children[0])
            self.traverse_cond(dana_cond.children[2])

        elif first_token.name == "p_expr":
            if len(dana_cond.children) == 1:
                expr_type = self.traverse_expr(first_token)
                if expr_type != DanaType("logic"):
                    print("Expression used in condition has no truth value")
            else:
                op1_type = self.traverse_expr(dana_cond.children[0])
                op2_type = self.traverse_expr(dana_cond.children[2])
                if op1_type != op2_type:
                    print("Type mismatch between expressions being compared. Types are {} and {}".format(op1_type, op2_type))
                elif op1_type not in [DanaType("int"), DanaType("byte")]:
                    print("Comparison between expressions of a nonordered type")
                

    def traverse_expr(self, dana_expr):
        first_token = dana_expr.children[0]
        if first_token == "LPAREN":
            return self.traverse_expr(dana_expr.children[1])


        elif first_token in ["PLUS", "MINUS"]:
            expr_type = self.traverse_expr(dana_expr.children[1])
            if expr_type != DanaType("int"):
                print("Unary sign operator applied to nonint expression")
            return expr_type


        elif first_token == "EXCLAMATION":
            expr_type = self.traverse_expr(dana_expr.children[1])
            if expr_type != DanaType("byte"):
                print("Negation operator ! applied to nonbyte expression")
            return expr_type
        elif first_token.name == "p_number":
            return DanaType("int")
        elif first_token.name == "p_char":
            return DanaType("byte")
        elif first_token.name == "p_string":
            return DanaType("byte", [0])
        elif first_token.name == "p_boolean":
            return DanaType("logic")
        elif first_token.name == "p_lvalue":
            return self.traverse_lvalue(first_token) 


        elif first_token.name == "p_expr":
            operation = dana_expr.children[1]
            if operation in ["PLUS", "MINUS", "STAR", "SLASH", "PERCENT"]:
                
                op1_type = self.traverse_expr(dana_expr.children[0])
                op2_type = self.traverse_expr(dana_expr.children[2])
                if op1_type != op2_type:
                    print("Type mismatch between expressions being compared. Types are {} and {}".format(op1_type, op2_type))
                elif op1_type not in [DanaType("int"), DanaType("byte")]:
                    print("Arithmetic operation between expressions of that are not of type int or byte")
            
                return op1_type

            elif operation in ["AMPERSAND", "VERTICAL"]:
                op1_type = self.traverse_expr(dana_expr.children[0])
                op2_type = self.traverse_expr(dana_expr.children[2])
                if op1_type != DanaType("byte") or op1_type != DanaType("byte"):
                    print("Logical operation between expressions that are not of type byte")
            
                return DanaType("logic")

                        

        elif first_token.name == "p_func_call":
            function_name = first_token.children[0]
            if not self.scope_stack.in_stack(function_name):
                print("Process {} not defined".format(function_name))
            definition_type = self.stack.first_type(dana_statement.children[0].value) 
            call_ops = traverse_call(dana_expr)

            if definition_type.ops != call_ops:
                print("Function {} not called with proper arguments".format(first_token.children[0].value))
            return DanaType(definition_type.base, definition_type.dimensions)

    def traverse_if_statement(self, dana_if_statement):
        unprocessed = deque(dana_elif_chain.children)
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_cond":
                    self.traverse_cond(child)


                elif child.name == "p_block": 
                    self.traverse_block(child)


                else:
                    self.extendleft_no_reverse(unprocessed, child.children) 
        
            except AttributeError:
                continue


    # Traverse statement block, checking its symbols against the current stack
    def traverse_block(self, dana_block):


        # Now the only thing we may find is names being used - no new declarations
        # So we check each one against the current scope stack
        unprocessed = deque([dana_block])
        while unprocessed:
            child = unprocessed.popleft()
            try:
                if child.name == "p_stmt":
                    self.traverse_statement(child) 


                else:
                    self.extendleft_no_reverse(unprocessed, child.children)
            except AttributeError:
                continue

        
    def check(self):
        self.get_function_scope(self.ast.children[0]) 
        

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
