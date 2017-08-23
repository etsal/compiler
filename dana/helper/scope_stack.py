from collections import deque as deque

class ScopeStack(object):
    def __init__(self, scopes = None):
        self.deque = deque(scopes) 


    def stack(self):
        return self.deque

    def top_scope(self):
        return self.stack()[0]

    def add_scope(self, scope = deque()):
        self.stack().appendleft(scope)

    def pop_scope(self):
        return self.stack().popleft()

 
    def print_top_scope(self):
        print(self.top_scope())

    def name_in_top_scope(self, name):
        return self.top_scope().name_in_scope(name)


    def print_stack(self):
        for scope in self.stack():
            print(scope)

    def name_in_stack(self, name):
        return any(scope.name_in_scope(name) for scope in self.stack())


    def push_symbol(self, symbol):
        self.top_scope().append(symbol)

    def push_symbols(self, symbols):
        self.top_scope().extend(symbols)


    def name_type(self, name):
        for scope in self.stack():
            if scope.name_in_scope(name):
                return scope.name_type(name)
        return None

    def __str__(self):
        string = "Stack: \n"
        for scope in self.stack():
            string += str(scope)
        return string
            
            
