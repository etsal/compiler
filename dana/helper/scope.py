from collections import deque as deque
from helper.type import DanaType as DanaType

class Scope(object):
    def __init__(self, parent = None, function_symbol = ("", DanaType("invalid")), symbols = [], labels = []):
        object.__setattr__(self, "is_immutable", False)
        self.parent=  parent
        self.function_symbol = function_symbol
        self.name = (parent.name if parent else "")+ "@" + function_symbol[0]
        self.type = function_symbol[1] 
        self.symbols = deque(symbols)
        self.args = []
        self.children = []
        self.labels = []


    def push_symbol(self, symbol):
        if self.is_immutable:
            raise ValueError("Changing an immutable object")
        
        self.symbols.append(symbol)

    def push_symbols(self, symbols):
        if self.is_immutable:
            raise ValueError("Changing an immutable object")
        
        self.symbols.extend(symbols)

    def name_in_scope(self, name):
        symbol_names = [x for (x,y) in self.symbols]
        return name in symbol_names      

    def name_type(self, name):
        return next((y for (x,y) in self.symbols if x == name), None)

    # An extra guarantee that after creation scopes stay static
    def make_immutable(self):
        self.is_immutable = True

    def __setattr__(self, name, value):
        if self.is_immutable:
            raise ValueError("Changing an immutable object")
        
        object.__setattr__(self, name, value)
 
   
    def __str__(self):
        if self.name is not None:
            string = "Function name: {}\n".format(self.name[0])
            string += "Function type: {}\n".format(self.name[1])
        else:
            string = "Function: ????????\n"
        for symbol in self.symbols:
            string += "Name: {}, Type: {}\n".format(symbol[0], symbol[1])
        string += "Labels: {}".format(self.labels)
        return string
       

        
