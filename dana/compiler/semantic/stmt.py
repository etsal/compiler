from compiler.semantic.symbol import Symbol as Symbol
from compiler.semantic.expr import DanaExpr as DanaExpr
from compiler.semantic.type import DanaType as DanaType

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

        d_child = d_stmt.multifind_first(self.optable.keys())
        name = d_child.name

        self.value = None
        self.label = None
        self.exprs = []
        self.operator = self.optable[name]

        verify[name](d_child, table)



    def verify_labeled(self, d_stmt, table):
        """Verifies a labeled (cont/break) statement against a symbol table"""
        d_label = d_stmt.find_first("p_name")
        if d_label:
            self.label = d_label.value
            table.check_table(d_stmt.linespan, Symbol(self.label, DanaType("label")))


    def verify_call(self, d_stmt, table):
        """Verifies a proc call statement against a symbol table"""
        d_exprs = d_stmt.find_all("p_expr")

        proc_name = d_stmt.find_first("p_name").value
        self.value = proc_name

        exprs = [DanaExpr.factory(d_expr, table) for d_expr in d_exprs]
        self.exprs = exprs

        actual = DanaType("void", args=[expr.type for expr in exprs])
        table.check_table(d_stmt.linespan, Symbol(proc_name, actual))



    def verify_ret(self, d_stmt, table):
        """Verifies a return statement against a symbol table"""
        d_expr = d_stmt.find_first("p_expr")
        self.exprs = [DanaExpr.factory(d_expr, table)] if d_expr else []

        expected = DanaType(table.function.type.base)
        ret_type = self.exprs[0].type if d_expr else DanaType("void")
        ret_type.check_type(d_stmt.linespan, expected)




    def verify_assign(self, d_stmt, table):
        """Verifies an assign statement against a symbol table"""
        lvalue = DanaExpr.factory(d_stmt.find_first_child("p_lvalue"), table)
        expr = DanaExpr.factory(d_stmt.find_first_child("p_expr"), table)
        self.exprs = [lvalue, expr]

        expr.type.check_type(d_stmt.linespan, lvalue.type)
        expr.type.in_types(d_stmt.linespan, [DanaType("int"), DanaType("byte")])

