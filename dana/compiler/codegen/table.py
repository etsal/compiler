class Table(dict):
    def __init__(self):
        super().__init__()
        self.funcs = dict() 
        self.breaks = dict()
        self.conts = dict()
        self.nexts = dict()
        self.globals = dict()
        self.access_link = 0
        self.offset = 0
        self.counter = 0
        self.mangled = dict()



    def new_name(self):
        name = "str" + str(self.counter)
        self.counter += 1
        return name
