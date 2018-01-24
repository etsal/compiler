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
    def __init__(self, symbol_table, dana_stmts):
        super().__init__()
        self.type = "basic"
        self.stmts = [DanaStmt(dana_stmt, symbol_table) for dana_stmt in dana_stmts]


class DanaLoop(DanaBlock):
    def __init__(self, symbol_table, dana_stmt):
        super().__init__()
        self.type = "loop"
        self.label = ""
        dana_label = dana_stmt.find_first_child("p_name")
        if dana_label:
            self.label = dana_label.value

        local_table = copy(symbol_table)
        local_table[self.label] = DanaType("label")

        dana_block = dana_stmt.find_first_child("p_block")
        self.block = DanaContainer(local_table, dana_block=dana_block)


class DanaIf(DanaBlock):

    def __init__(self, symbol_table, dana_stmt):
        super().__init__()
        self.type = "if"
        dana_cond = dana_stmt.find_first_child("p_cond")
        self.cond = DanaExpr(dana_cond, symbol_table)

        dana_block_if = dana_stmt.find_first_child("p_block")
        self.if_path = DanaContainer(symbol_table, dana_block=dana_block_if)
        self.else_path = None

        dana_elif = dana_stmt.find_first_child("p_elif_chain")
        if dana_elif:
            if dana_elif.find_first_child("p_cond"):
                self.else_path = \
                    DanaIf(symbol_table, dana_stmt=dana_elif)
            else:

                dana_block = dana_elif.find_first_child("p_block")
                self.else_path = \
                    DanaContainer(symbol_table, dana_block=dana_block)



class DanaContainer(DanaBlock):
    def __init__(self, symbol_table, dana_block):
        super().__init__()
        self.type = "container"
        basic_block = []
        self.children = []
        dana_stmts = dana_block.find_all("p_stmt")
        for dana_stmt in dana_stmts:
            if dana_stmt.multifind_children(["p_assign_stmt", "p_proc_call", "p_skip_stmt"]):
                basic_block.append(dana_stmt)

            else:
                if basic_block:
                    dana_stmts_children = [dana_stmt for dana_stmt in basic_block]
                    self.children += \
                        [DanaBasic(symbol_table, dana_stmts=dana_stmts_children)]
                    basic_block = []

                dana_loop_stmt = dana_stmt.find_first_child("p_loop_stmt")
                dana_if_stmt = dana_stmt.find_first_child("p_if_stmt")
                dana_terminator_stmt = dana_stmt.multifind_children(["p_continue_stmt", "p_ret_stmt", "p_break_stmt"])
                if dana_loop_stmt:
                    self.children += [DanaLoop(symbol_table, dana_stmt=dana_loop_stmt)]

                elif dana_if_stmt:
                    self.children += [DanaIf(symbol_table, dana_stmt=dana_if_stmt)]

                elif dana_terminator_stmt:
                    basic_block.append(dana_stmt)
                    dana_stmts_children = [dana_stmt for dana_stmt in basic_block]
                    self.children += \
                        [DanaBasic(symbol_table, dana_stmts=dana_stmts_children)]
                    basic_block = []

        if basic_block:
            dana_stmts_children = [dana_stmt for dana_stmt in basic_block]
            self.children += \
                [DanaBasic(symbol_table, dana_stmts=dana_stmts_children)]
            basic_block = []
