class DanaFunction(object):
    def __init__(self, parent, symbol, defs, args, block):
        self.parent = parent 
        self.symbol = symbol
        self.defs = defs 
        self.args = args 
        self.block = block 

        self.children = []

    def __str__(self):
        ret = "-------{}-------\n".format(str(self.symbol)) 
        ret += "Args: {}\n".format([str(arg) for arg in self.args])
        ret += "Defs: {}\n".format([str(dana_def) for dana_def in self.defs])
        ret += "Parent: {}\n".format(str(self.parent.symbol) if self.parent else "")
        ret += "Children: {}\n".format(str([str(child.symbol) for child in self.children]))
        return ret
