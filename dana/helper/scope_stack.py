from collections import deque as deque

class ScopeStack(object):
    def __init__(self, ast = None):
        self.stack = deque() 
        self.ast = ast


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


    def in_scope(self, symbol, scope):
        symbol_names = [x for (x,y) in scope]
        return symbol in symbol_names      

    def in_current_scope(self, symbol):
        return self.in_scope(symbol, self.stack[0])

    def in_stack(self, symbol):
        return any(self.in_scope(self, symbol, scope) for scope in self.stack)

