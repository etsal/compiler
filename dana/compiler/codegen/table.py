class Table(dict):
    def __init__(self):
        super().__init__()
        self.funcs = dict() 
        self.breaks = dict()
        self.conts = dict()
        self.nexts = dict()


    def __copy__(self):
        new_table = Table() 

        new_table.funcs = copy(self.funcs)

        for key in self.keys():
            new_table[key] = self[key]

        return new_table
