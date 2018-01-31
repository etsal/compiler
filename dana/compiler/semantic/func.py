from compiler.semantic.table import Symbol

class DanaFunction(object):
    def __init__(self, parent, table, block):
        self.parent = parent
        self.table = table
        self.block = block
        self.children = []

    @property
    def mangled(self):
        name = self.symbol.name
        if self.parent:
            name = self.parent.mangled.name + "$" + self.symbol.name

        return Symbol(name, self.symbol.type)

    @property
    def symbol(self):
        return self.table.function

    def return_specific(self, stype):
        return [name for name in self.table.stype.keys() if self.table.stype[name] == stype]


    @property
    def parents(self):
        return self.return_specific("parent")

    @property
    def defs(self):
        return self.return_specific("def")

    @property
    def args(self):
        return self.table.args_ordered

    @property
    def funcs(self):
        return self.return_specific("func")

    def __str__(self):
        ret = "-------{}-------\n".format(str(self.symbol))
        ret += "Args: {}\n".format([str(arg) for arg in self.args])
        ret += "Defs: {}\n".format([str(d_def) for d_def in self.defs])
        ret += "Parent: {}\n".format(str(self.parent.symbol) if self.parent else "")
        ret += "Children: {}\n".format(str([str(child.symbol) for child in self.children]))
        return ret
