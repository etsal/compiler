from compiler.semantic.symbol import Symbol as Symbol

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

    @property
    def parents(self):
        return self.table.parents

    @property
    def defs(self):
        return self.table.defs

    @property
    def args(self):
        return self.table.args

    def __str__(self):
        ret = "-------{}-------\n".format(str(self.symbol))
        ret += "Args: {}\n".format([str(arg) for arg in self.args])
        ret += "Defs: {}\n".format([str(d_def) for d_def in self.defs])
        ret += "Parent: {}\n".format(str(self.parent.symbol) if self.parent else "")
        ret += "Children: {}\n".format(str([str(child.symbol) for child in self.children]))
        return ret
