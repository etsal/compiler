from compiler.semantic.symbol import Symbol as Symbol
from compiler.semantic.expr import DanaExpr as DanaExpr
from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.error import *

class DanaStmt(object):
    optable = dict({"p_cont_stmt" : "continue",
                   "p_break_stmt" : "break", 
                   "p_proc_call" : "call",
                   "p_ret_stmt" : "ret",
                   "p_assign_stmt" : "assign",
                  })


    def __init__(self, d_stmt, table):

        verify = dict({"p_cont_stmt" : self.verify_labeled,
                       "p_break_stmt" : self.verify_labeled,
                       "p_proc_call" : self.verify_call,
                       "p_ret_stmt" : self.verify_ret,
                       "p_assign_stmt" : self.verify_assign,
                      })

        d_child = d_stmt.multifind_first(verify.keys())
        name = d_child.name

        self.value = None
        self.label = None
        self.exprs = []
        self.operator = self.optable[name]

        verify[name](d_child, table)



    def verify_labeled(self, d_stmt, table):
        d_label = d_stmt.find_first("p_name")
        if d_label:
            label = Symbol(d_label.value, DanaType("label"))
            check_table(d_stmt.linespan, label, table)
            self.label = label.name


    def verify_call(self, d_stmt, table):

        d_exprs = d_stmt.find_all("p_expr")
        exprs = [DanaExpr.factory(d_expr, table) for d_expr in d_exprs]
        types = [expr.type for expr in exprs]

        proc_name = d_stmt.find_first("p_name").value
        actual = DanaType("void", args=types)
        check_table(d_stmt.linespan, Symbol(proc_name, actual), table)

        self.value = proc_name
        self.exprs = exprs



    def verify_ret(self, d_stmt, table):
        expected = DanaType(table.function.type.base)
        actual = DanaType("void")

        d_expr = d_stmt.find_first("p_expr")
        exprs = []
        if d_expr:
            exprs += [DanaExpr.factory(d_expr, table)]
            actual = exprs[0].type

        actual.check_type(d_stmt.linespan, expected)

        self.exprs = exprs



    def verify_assign(self, d_stmt, table):
        lvalue = DanaExpr.factory(d_stmt.find_first_child("p_lvalue"), table)
        expr = DanaExpr.factory(d_stmt.find_first_child("p_expr"), table)

        expected = lvalue.type
        actual = expr.type
        actual.check_type(d_stmt.linespan, expected)
        actual.in_types(d_stmt.linespan, [DanaType("int"), DanaType("byte")])

        self.exprs = [lvalue, expr]
