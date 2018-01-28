class Table(dict):
    def __init__(self):
        super().__init__()
        self.stype = dict()
        self.referenced = set() 
        self.function = None
        self.args_ordered = []

    def __getitem__(self, key):
        if key and key in self.keys() and self.stype[key] == "parent":
            self.referenced.add(key)
        return super().__getitem__(key)

    def register(self, symbols, stype):
        for symbol in symbols:
            self[symbol.name] = symbol.type
            self.stype[symbol.name] = stype
 

    def extend_decls(self, decls):
        self.register(decls, "decl")


    def extend_defs(self, defs):
        self.register(defs, "def")


    def extend_funcs(self, funcs):
        self.register(funcs, "func")


    def extend_args(self, args):
        self.register(args, "arg")
        self.args_ordered += [symbol.name for symbol in args]

    def __copy__(self):
        new_table = Table() 

        for name in self.stype:
            if self.stype[name] == "func":
                new_table.stype[name] = "func"
            else:
                new_table.stype[name] = "parent" 

        new_table.function = self.function

        for key in self.keys():
            new_table[key] = super().__getitem__(key)

        return new_table
