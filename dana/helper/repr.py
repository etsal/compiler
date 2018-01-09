from helper.node import * 

class Symbol(object):
    def __init__(self, name, dana_type):
        self.name = name
        self.type = dana_type

    def __str__(self):
       return "({},{})".format(self.name, self.type) 

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __ne__(self, other):
        return not __eq__(self, other)

class DanaFunction(object):
    def __init__(self, parent, symbol, defs, args, block):
        self.parent = parent 
        self.symbol = symbol
        self.defs = defs 
        self.args = args 
        self.block= block 

        self.children = []

    def __str__(self):
        ret = "-------{}-------\n".format(str(self.symbol)) 
        ret += "Args: {}\n".format([str(arg) for arg in self.args])
        ret += "Defs: {}\n".format([str(dana_def) for dana_def in self.defs])
        ret += "Parent: {}\n".format(str(self.parent.symbol) if self.parent else "")
        ret += "Children: {}\n".format(str([str(child.symbol) for child in self.children]))
        return ret

class DanaBlock(object):
    def __init__(self, dana_block):
        self.stmts = dana_block.find_all("p_stmt")
        self.children = []
        basic_block = []
        for stmt in self.stmts:
            if not stmt.multifind(["p_loop_stmt", "p_if_stmt"]):
                basic_block.append(stmt)
            else:
                if basic_block: 
                    self.children.append(DanaBasicBlock(basic_block))
                    basic_block = []
                if stmt.find_first_child("p_loop_stmt"):
                    self.children.append(DanaLoopBlock(stmt))
                elif stmt.find_first_child("p_if_stmt"):
                    self.children.append(DanaIfBlock(stmt))
        if basic_block: 
            self.children.append(DanaBasicBlock(basic_block))
            basic_block = []
        self.stmts = None
        self.label = None
        self.conds = None

class DanaBasicBlock(object):
    def __init__(self, stmts):
        self.stmts = stmts
        self.children = None
        self.label = None
        self.conds = None

class DanaIfBlock(object):
    def __init__(self, dana_block):
        components = dana_block.multifind(["p_cond", "p_block"])
        self.conds = [comp for comp in components if comp.name == "p_cond"]
        self.children = [DanaBlock(comp) for comp in components if comp.name == "p_block"]
        self.label = None
        self.conds = None
        self.stmts = None
        

class DanaLoopBlock(object):
    def __init__(self, dana_block):
        self.label = dana_block.find_first_child("p_name")
        self.children= [DanaBlock(dana_block.find_first("p_block"))]
        self.stmts = None
        self.conds = None
