from compiler.semantic.expr import DanaExpr as DanaExpr
from compiler.semantic.type import DanaType as DanaType

class DanaStmt(object):
    def __init__(self, dana_stmt, symbol_table):
        self.label = None 
        self.exprs = [] 
        self.operation = None 

        if dana_stmt.multifind(["p_cont_stmt", "p_break_stmt"]):
            self.verify_labeled_stmt(dana_stmt, symbol_table)
        elif dana_stmt.find_first_child("p_proc_call"):
            self.verify_call_stmt(dana_stmt, symbol_table)
        elif dana_stmt.find_first_child("p_ret__stmt"):
            self.verify_ret_stmt(dana_stmt, symbol_table)
        elif dana_stmt.find_first_child("lvalue"):
            self.verify_assign_stmt(dana_stmt, symbol_table)



    def verify_labeled_stmt(self, stmt, symbol_table):
        label = stmt.find_first("p_name")
        if label:
            label = label.value
            if label not in symbol_table:
                print("Lines {}: Label {} not defined in current scope".format(stmt.linespan, label))
            elif symbol_table[label] != DanaType("label"):
                print("Lines {}: Symbol {} not not a label".format(stmt.linespan, label))
        
        operation = None
        if stmt.name == "p_cont_stmt":
            operation = "continue" 
        elif stmt.name == "p_break_stmt":
            operation = "break"

        self.label = label
        self.operation = operation
        


    def verify_call_stmt(self, stmt, symbol_table):
        proc_name = stmt.find_first("p_name").value
        if proc_name not in symbol_table:
            print("Lines {}: Symbol {} not in scope".format(stmt.linespan, proc_name))
            return 
            
        dana_exprs = stmt.find_all("p_expr")
        exprs = [DanaExpr(dana_expr, symbol_table) for dana_expr in dana_exprs]
        types = [expr.type for expr in exprs]

        expected_type = symbol_table[proc_name] if proc_name in symbol_table else DanaType("invalid")
        actual_type = DanaType("void", args = types)
        if expected_type != actual_type:
            print("Lines {}: Proc has type {} but called as {}".format(stmt.linespan, str(expected_type), str(actual_type)))
            
        
        self.exprs = exprs
        self.operation = "call"
        


    def verify_ret_stmt(self, stmt, symbol_table):    
        expected_type = DanaType(symbol_table["$"].base)
        actual_type = DanaType("void")

        dana_expr = stmt.find_first("p_expr")
        exprs = [] 
        if dana_expr:
            exprs += [DanaExpr(expr, symbol_table)] 
            actual_type = exprs[0].type

        if expected_type != actual_type:
            print("Lines {}: Function has type {} but returns {}".format(stmt.linespan, expected_type, actual_type))

        self.exprs = exprs 
        self.operation = "ret"
      


    def verify_assign_stmt(stmt, symbol_table):
        lvalue = DanaExpr(stmt.get_first_child("p_lvalue"), symbol_table)
        expr = DanaExpr(stmt.get_first_child("p_expr"), symbol_table)

        expected_type = lvalue.type 
        actual_type = expr.type
        if expected_type != actual_type:
            print("Lines {}: Function has type {} but returns {}".format(stmt.linespan, expected_type, actual_type))


        self.exprs = [lvalue, expr]
        self.operation = "assign"







