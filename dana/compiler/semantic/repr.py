from copy import copy

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
    def __init__(self, dana_block = None, stmts = None, children = [], label = None, conds = None):
        self.stmts = [stmt for stmt in stmts] if stmts else None
        self.children = [child for child in children] if children else []
        self.label = label 
        self.conds = conds 

        if not dana_block:
            return

        dana_stmts = dana_block.find_all("p_stmt")
        basic_block = []
        for stmt in dana_stmts:
            if not stmt.multifind_children(["p_loop_stmt", "p_if_stmt"]):
                basic_block.append(stmt)
            else:
                if basic_block: 
                    
                    child_stmts = [stmt for stmt in basic_block]
                    self.children += [DanaBlock(stmts = child_stmts)]
                    basic_block = []
                    
                if stmt.find_first_child("p_loop_stmt"):

                    loop_label = None
                    dana_label = stmt.find_first_child("p_name")
                    if loop_label:
                       loop_label = dana_label.value 
                    loop_block = stmt.find_first("p_block")
                    self.children += [DanaBlock(dana_block = loop_block, label = loop_label)]
                elif stmt.find_first_child("p_if_stmt"):

                    components = stmt.multifind(["p_cond", "p_block"])
                    if_conds = [comp for comp in components if comp.name == "p_cond"]
                    if_children = [DanaBlock(dana_block = comp) for comp in components if comp.name == "p_block"]
                    self.children += [DanaBlock(children = if_children, conds = if_conds)]

        if basic_block: 
            child_stmts = [stmt for stmt in basic_block]
            self.children += [DanaBlock(stmts = child_stmts)]
            basic_block = []


 
    def __eq__(self, other):
        return self.label == other.label and self.conds == other.conds and self.children == other.children and self.stmts == other.stmts


    def __ne__(self,other):
        return not __eq__(self, other)


    def __str__(self):


        ret = "\n======BEGIN=FUN======\n"
        if self.label:
            ret += "Label: {}".format(self.label)

        if self.conds:
            ret += "\n-------Conds-------\n"
            for cond in self.conds:
                ret += str(cond)

        if self.stmts:
            ret += "\n-------Stmts-------\n"
            for stmt in self.stmts:
                ret += str(stmt)

        if self.children:
            ret += "\n-------Children-------\n"
            for child in self.children:
                ret += str(child)
        
        ret += "\n======END===FUN======\n"
    

        return ret
