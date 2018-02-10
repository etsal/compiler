class AddressTable(dict):
    def __init__(self, gtable):
        super().__init__()
        self.breaks = dict()
        self.conts = dict()
        self.nexts = dict()
        self.mangles = dict()
        self.gtable = gtable
        self.current = None
       
    @property
    def funcs(self):
        return self.gtable.funcs

    @property
    def strings(self):
        return self.gtable.strings 




class FuncInfo(object):
    def __init__(self, func, args):
        self.func = func
        self.args = args
        

class GlobalTable(object):
    def __init__(self): 
        self.funcs = dict()
        self.counter = 0
        self.strings = dict()
        

    def new_name(self):
        name = "str" + str(self.counter)
        self.counter += 1
        return name
