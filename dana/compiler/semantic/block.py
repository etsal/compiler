from copy import copy
from compiler.semantic.stmt import DanaStmt as DanaStmt
from compiler.semantic.expr import DanaExpr as DanaExpr
from compiler.semantic.type import DanaType as DanaType

class DanaBlock(object):
    def __init__(self):
        self.label = ""
        self.cond = None
        self.children = None
        self.stmts = None

    def __eq__(self, other):
        return self.label == other.label and \
               self.cond == other.cond and \
               self.children == other.children and \
               self.stmts == other.stmts


    def __ne__(self, other):
        return not self.__eq__(self, other)




class DanaBasic(DanaBlock):
    def __init__(self, symbol_table, d_stmts):
        super().__init__()
        self.type = "basic"
        self.stmts = [DanaStmt(d_stmt, symbol_table) for d_stmt in d_stmts]


class DanaLoop(DanaBlock):
    def __init__(self, symbol_table, d_stmt):
        super().__init__()
        self.type = "loop"
        self.label = ""
        d_label = d_stmt.find_first_child("p_name")
        if d_label:
            self.label = d_label.value

        local_table = copy(symbol_table)
        local_table[self.label] = DanaType("label")

        d_block = d_stmt.find_first_child("p_block")
        self.block = DanaContainer(local_table, d_block=d_block)


class DanaIf(DanaBlock):

    def __init__(self, symbol_table, d_stmt):
        super().__init__()
        self.type = "if"
        d_cond = d_stmt.find_first_child("p_cond")
        self.cond = DanaExpr.factory(d_cond, symbol_table)

        d_block_if = d_stmt.find_first_child("p_block")
        self.if_path = DanaContainer(symbol_table, d_block=d_block_if)
        self.else_path = None

        d_elif = d_stmt.find_first_child("p_elif_chain")
        if d_elif:
            if d_elif.find_first_child("p_cond"):
                self.else_path = \
                    DanaIf(symbol_table, d_stmt=d_elif)
            else:

                d_block = d_elif.find_first_child("p_block")
                self.else_path = \
                    DanaContainer(symbol_table, d_block=d_block)



class DanaContainer(DanaBlock):
    def __init__(self, symbol_table, d_block):
        super().__init__()
        self.type = "container"
        basic_block = []
        self.children = []
        d_stmts = d_block.find_all("p_stmt")
        for d_stmt in d_stmts:
            if d_stmt.multifind_children(["p_assign_stmt", "p_proc_call", "p_skip_stmt"]):
                basic_block.append(d_stmt)

            else:
                if basic_block:
                    d_stmts_children = [d_stmt for d_stmt in basic_block]
                    self.children += \
                        [DanaBasic(symbol_table, d_stmts=d_stmts_children)]
                    basic_block = []

                d_loop_stmt = d_stmt.find_first_child("p_loop_stmt")
                d_if_stmt = d_stmt.find_first_child("p_if_stmt")
                d_terminator_stmt = d_stmt.multifind_children(["p_continue_stmt", "p_ret_stmt", "p_break_stmt"])
                if d_loop_stmt:
                    self.children += [DanaLoop(symbol_table, d_stmt=d_loop_stmt)]

                elif d_if_stmt:
                    self.children += [DanaIf(symbol_table, d_stmt=d_if_stmt)]

                elif d_terminator_stmt:
                    basic_block.append(d_stmt)
                    d_stmts_children = [d_stmt for d_stmt in basic_block]
                    self.children += \
                        [DanaBasic(symbol_table, d_stmts=d_stmts_children)]
                    basic_block = []

        if basic_block:
            d_stmts_children = [d_stmt for d_stmt in basic_block]
            self.children += \
                [DanaBasic(symbol_table, d_stmts=d_stmts_children)]
            basic_block = []
