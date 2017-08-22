from collections import deque as deque

class ScopeStack(object):
    def __init__(self, ast = None):
        self.stack = deque() 
        self.ast = ast
        self.functions = deque()


    def add_scope(self, function = None):
        self.stack.appendleft(deque())
        self.functions.appendleft(function)

    def pop_scope(self):
        self.functions.popleft()
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


    def in_scope(self, name, scope):
        symbol_names = [x for (x,y) in scope]
        return name in symbol_names      

    def in_current_scope(self, name):
        return self.in_scope(name, self.stack[0])

    def in_stack(self, name):
        return any(self.in_scope(self, name, scope) for scope in self.stack)

    def top_scope():
        return self.stack[0]

    def all_scopes():
        return self.stack

    def top_function():
        return self.functions[0]

    def symbol_type(self, symbol, scope):
        symbol_type = [y for (x,y) in scope if symbol == x]
        if len(symbol_type) > 0:
            return symbol_type[0]
        else:
            return None
            
    def first_type(self, name):
        for scope in self.all_scopes():
            maybe_type =  self.symbol_type(name, scope)
            if maybe_type is not None:
                return maybe_type
        return None
