from collections import deque as deque

class Scope(object):
    def __init__(self, main = None, symbols = [], labels = []):
        self.symbols = deque(symbols)
        self.main = main
        self.labels = []


    def push_symbol(self, symbol):
        self.symbols.append(symbol)

    def push_symbols(self, symbols):
        self.symbols.extend(symbols)


    def name_in_scope(self, name):
        symbol_names = [x for (x,y) in self.symbols]
        return name in symbol_names      

    def name_type(self, name):
        return next((y for (x,y) in self.symbols if x == name), None)

   
    def __str__(self):
        if self.main is not None:
            string = "Function name: {}\n".format(self.main[0])
            string += "Function type: {}\n".format(self.main[1])
        else:
            string = "Function: ????????\n"
        for symbol in self.symbols:
            string += "Name: {}, Type: {}\n".format(symbol[0], symbol[1])
        string += "Labels: {}".format(self.labels)
        return string
       

        
