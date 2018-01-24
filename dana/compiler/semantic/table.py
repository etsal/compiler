class Table(dict):
    def __init__(self):
        super().__init__()
        self.args = [] 
        self.defs = [] 
        self.decls = []
        self.funcs = []


    def register(self, symbols):
        for symbol in symbols:
           self[symbol.name] = symbol.type


    def extend_decls(self, decls):
        self.decls += decls
        self.register(decls)


    def extend_defs(self, defs):
        self.defs += defs
        self.register(defs)


    def extend_funcs(self, funcs):
        self.funcs += funcs
        self.register(funcs)


    def extend_args(self, args):
        self.args += args
        self.register(args)

    def __copy__(self):
        new_table = Table() 

        new_table.extend_decls(self.decls)
        new_table.extend_defs(self.defs)
        new_table.extend_funcs(self.funcs)
        new_table.extend_args(self.args)

        for key in self.keys():
            new_table[key] = self[key]

        return new_table
