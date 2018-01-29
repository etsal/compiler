class Table(dict):

    class ScopeError(Exception):
        pass

    def __init__(self):
        super().__init__()
        self.stype = dict()
        self.referenced = set()
        self.function = None
        self.args_ordered = []

    def __getitem__(self, key):
        """
        Overload item accesses to keep track of the accesses of symbols
        of the current scope
        """
        if key and key in self.keys() and self.stype[key] == "parent":
            self.referenced.add(key)
        return super().__getitem__(key)


    def check_scope(self, line, name):
        """Check for the existence of a symbol"""
        if name not in self:
            raise self.ScopeError("L {}: Unknown symbol {}".format(line, name))

    def check_absent(self, line, name):
        """Check for the absence of a symbol"""
        if name in self:
            raise self.ScopeError("L {}: Double definition {}".format(line, name))

    def check_table(self, line, symbol):
        """Check for the existence and DanaType of a symbol"""
        self.check_scope(line, symbol.name)
        expected = self[symbol.name]
        symbol.type.check_type(line, expected)

    def check_conflicts(self, line, name, stype):
        """Check for invalid multiple definitions of a symbol"""
        try:
            self.check_absent(line, name)
        except self.ScopeError:
            old_stype = self.stype[name]
            if old_stype == "parent":
                pass
            # Check if it's a decl/def pair (in that order)
            elif old_stype == "decl" and stype != "func":
                self.check_absent(line, name)


    def register(self, symbols, stype):
        """Put the symbol in the dict, along with its symbol type"""
        for symbol in symbols:
            self[symbol.name] = symbol.type
            self.stype[symbol.name] = stype

    def extend_decls(self, decls):
        """Register the symbols in the list as function declarations"""
        self.register(decls, "decl")

    def extend_defs(self, defs):
        """Register the symbols in the list as variable definitions"""
        self.register(defs, "def")

    def extend_funcs(self, funcs):
        """Register the symbols in the list as function definitions"""
        self.register(funcs, "func")

    def extend_args(self, args):
        """Register the symbols in the list as argument definitions"""
        self.register(args, "arg")

        # We need the order to check the types of function call arguments
        self.args_ordered += [symbol.name for symbol in args]

    def __copy__(self):
        """
        Copy function that changes the stypes of the contents
        to show that they have been inherited by the parent scope
        """
        new_table = Table()

        # FIXME: Maybe making functions global will be a problem by shadowing?
        for name in self.stype:
            if self.stype[name] == "func":
                new_table.stype[name] = "func"
            else:
                new_table.stype[name] = "parent"

        new_table.function = self.function

        for key in self.keys():
            new_table[key] = super().__getitem__(key)

        return new_table
