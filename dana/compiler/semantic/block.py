from compiler.semantic.stmt import DanaStmt as DanaStmt
from compiler.semantic.expr import DanaExpr as DanaExpr
from compiler.semantic.type import DanaType as DanaType

class DanaBlock(object):
    def __init__(self):
        self.label = ""
        self.cond = None
        self.children = []
        self.stmts = None

    def __eq__(self, other):
        return self.label == other.label and \
               self.cond == other.cond and \
               self.children == other.children and \
               self.stmts == other.stmts


    def __ne__(self, other):
        return not self.__eq__(self, other)




class DanaBasic(DanaBlock):
    """Dana basic block"""
    def __init__(self, table, d_stmts):
        super().__init__()
        self.type = "basic"
        self.stmts = [DanaStmt(d_stmt, table) for d_stmt in d_stmts]


class DanaLoop(DanaBlock):
    """Dana loop block, holds the subblocks making up the loop"""
    def __init__(self, table, d_stmt):
        super().__init__()
        self.type = "loop"

        d_label = d_stmt.find_first_child("p_name")
        label = d_label.value if d_label else ""
        self.label = label

        # Labels are the _only_ symbol that can be defined in a block,
        # so we handle their definitions here
        tmp_label = None
        if label in table:
            if table.stype[label] != "parent":
                table.check_absence(d_label.linespan, label)

        if label:
            tmp_label = table[label]
            table[label] = DanaType("label")


        d_block = d_stmt.find_first_child("p_block")
        self.block = DanaContainer(table, d_block=d_block)

        if label:
            table[label] = tmp_label



class DanaIf(DanaBlock):
    """
    Dana if block, holds the subblocks and conditions
    making up the if statement. In case of an elif chain,
    we treat the latter as an else statement and store it
    in our else path
    """
    def __init__(self, table, d_stmt):
        super().__init__()
        self.type = "if"

        # The condition and block for this part of the branch
        d_cond = d_stmt.find_first_child("p_cond")
        self.cond = DanaExpr.factory(d_cond, table)

        d_if = d_stmt.find_first_child("p_block")
        self.if_path = DanaContainer(table, d_block=d_if)
        self.else_path = None

        # For elif chains (which can also be just an else block),
        # we fill up the else path
        d_elif = d_stmt.find_first_child("p_elif_chain")
        if d_elif:
            # Elif chain
            if d_elif.find_first_child("p_cond"):
                self.else_path = DanaIf(table, d_stmt=d_elif)
            # Else block
            else:
                d_block = d_elif.find_first_child("p_block")
                self.else_path = DanaContainer(table, d_block=d_block)



class DanaContainer(DanaBlock):
    """
    Dana block container, holds a sequence of blocks.
    Used to structure the blocks as a tree
    """
    def __init__(self, table, d_block):
        super().__init__()
        self.type = "container"

        basic_block = []
        d_stmts = d_block.find_all("p_stmt")
        for d_stmt in d_stmts:
            # We keep on adding into the current basic block
            if d_stmt.multifind_children(["p_assign_stmt", "p_proc_call", "p_skip_stmt"]):
                basic_block.append(d_stmt)

            else:
                d_terminator = d_stmt.multifind_children(["p_continue_stmt",
                                                          "p_ret_stmt",
                                                          "p_break_stmt"
                                                         ])

                if d_terminator:
                    basic_block.append(d_stmt)

                # We close up the block, since we found a terminator
                if basic_block:
                    self.children += [DanaBasic(table, d_stmts=basic_block)]
                    basic_block = []

                d_loop = d_stmt.find_first_child("p_loop_stmt")
                if d_loop:
                    self.children += [DanaLoop(table, d_stmt=d_loop)]

                d_if = d_stmt.find_first_child("p_if_stmt")
                if d_if:
                    self.children += [DanaIf(table, d_stmt=d_if)]


        if basic_block:
            self.children += [DanaBasic(table, d_stmts=basic_block)]
            basic_block = []
