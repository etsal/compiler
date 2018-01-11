from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.symbol import Symbol as Symbol

class DanaExpr(object):

    operators = ["const", "id", 
                 "lvalue", "call", 
                 "neg", "!",
                 "+", "-", "*", "/", "%",
                 "&", "|", 
                 "and", "or", "not",
                 "=", "!=", "<", "<=", ">=", ">",
                ]

    def __init__(self, dana_expr, symbol_table):
        self.type = DanaType("invalid") 
        self.value = None
        self.operator = None
        self.children = []
         
        #Hacky
        if dana_expr.name == "p_cond":
            dana_expr = dana_expr.children[0]

        const = dana_expr.multifind_children(["p_number", "p_char", "p_boolean"])
        if const:
            self._make_const_expr(const[0])
            return 
        
        dana_func_call = dana_expr.find_first_child("p_func_call")
        if dana_func_call:
            self._make_func_call(dana_func_call, symbol_table)
            return 


        dana_lvalue = dana_expr.find_first_child("p_lvalue")
        if dana_expr.name == "p_lvalue": 
            dana_lvalue = dana_expr
        if dana_lvalue:
            self._make_lvalue(dana_lvalue, symbol_table)
            return

        args = dana_expr.multifind(["p_expr", "p_cond"])
        if len(args) == 1:
            self._make_unary(dana_expr.children[0], args[0], symbol_table) 
            return

        elif len(args) == 2:
            self._make_binary(dana_expr.children[1], args[0], args[1], symbol_table)
            return
    
        else:
            print("ERROR: INVALID EXPRESSION")

        print("ERROR: INVALID EXPRESSION")
            
        
        
        
    def _make_const_expr(self, const): 
        self.type = DanaType("int") if const.name == "p_number" else DanaType("byte") 
        if const.value in ["true", "false"]:
            self.value = 1 if const.value == "true" else 0
        else:
            self.value = const.value
        self.operator = "const"
        return

    def _make_func_call(self, dana_func_call, symbol_table):
        name = dana_func_call.find_first_child("p_name").value
        if not name in symbol_table:
            print("Lines {}: Symbol {} not in scope".format(dana_func_call.linespan, name))
            return
        else:
            expected_args = symbol_table[name].args
            if expected_args is None:
                print("Lines {}: Nonfunction called as function", dana_func_call.linespan, name)
                return
            exprs = [DanaExpr(dana_expr, symbol_table) for dana_expr in dana_func_call.find_all("p_expr")]
            types = [expr.type for expr in exprs]
            if expected_args != types:
                print("Lines {}: Arguments {} in function call {} instead of {} ".format(dana_func_call.linespan, [str(t) for t in types], name, [str(t) for t in expected_args]))
        

        self.type = DanaType(symbol_table[name].base)
        self.value = name
        self.operator = "call"
        return


    def _make_unary(self, operator, operand, symbol_table):
        child = DanaExpr(operand, symbol_table)
        if operator in ["(", "+"]:
    
            if child.type != DanaType("int") and operator == "+":
                print("Lines {}: Operator {} for expression {}", operator, str(child.type)) 
                return 

            self.children.append(child)         
            self.type = child.type
            self.operator = "id"
            return

        if (operator == "!" and child.type != DanaType("byte")) or \
           (operator == "-" and child.type != DanaType("int")) or \
           (operator == "not" and child.type != DanaType("logic")):
            print("Lines {}: Operator {} for expression {}", operator, str(child.type)) 

        self.children.append(child)         
        self.operator = "neg" if operator == "-" else operator
        self.type = child.type
        return

    
    def _make_binary(self, operator, arg1, arg2, symbol_table): 
        op1 = DanaExpr(arg1, symbol_table) 
        op2 = DanaExpr(arg2, symbol_table) 
        if op1.type != op2.type:
            print("Lines {},{}: Operands {} and {}".format(arg1.linespan, arg2.linespan, str(op1.type), str(op2.type))) 
            return


        if operator in ["+", "-", "STAR", "SLASH", "PERCENT", "<", "<=", ">=", ">", "=", "!="] and not op1.type in [DanaType("int"), DanaType("byte")]:
            print("Lines {},{}: Operands {} for arithmetic operation", arg1.linespan, arg2.linespan, str(self.type)) 
            return

        if operator in ["&", "|"] and op1.type != DanaType("byte"):
            print("Lines {},{}: Operands {} for byte operation", arg1.linespan, arg2.linespan, str(self.type)) 
            return
 

        if operator in ["and", "or"] and not op1.type in [DanaType("logic"), DanaType("byte"), DanaType("int")]:
            print("Lines {},{}: Operands {} for logic operation", arg1.linespan, arg2.linespan, str(self.type)) 

        new_names = dict({"STAR" : "*", "SLASH" : "/", "PERCENT" : "%"})

        self.children += [op1, op2] 
        self.type = op1.type
        self.operator = new_names[operator] if operator in new_names else operator

        if not self.operator in self.operators:
            print("INVALID BINARY OPERATOR " + self.operator)


    def _make_lvalue(self, dana_lvalue, symbol_table):
        string = dana_lvalue.find_first_child("p_string")
        if string:
            self.type = DanaType("byte", dims = [len(string.value) + 1])
            self.value = string.value
            self.operator = "const"
            return

        name = dana_lvalue.find_first_child("p_name").value
        if name:
            if name not in symbol_table:
                print("Lines {}: Symbol {} not in scope".format(dana_lvalue.linespan, name))
                return

            self.value = name
            self.type = symbol_table[name]
            self.operator= "lvalue"
            return

        
        expr = stmt.find_first_child("p_expr")
        if expr:
            expr = DanaExpr(expr, symbol_table) 
            if expr.type != DanaType("int"):
                print("Lines {}: Type {} used as index".format(dana_lvalue.linespan, expr.type))
                return
    
            child_lvalue = lvalue.find_first_child("p_lvalue")
            child = DanaExpr(child_lvalue, symbol_table)
            if not child_type.dims:
                print("Lines {}: Base type {} dereferenced".format(child_lvalue.linespan, child.type))
                return
            
            self.children = [child]
            self.type = DanaType(child.type.base, dims = child.type.dims[1:], args = child.type.ops)
            self.operator = "lvalue"
            return




    def __str__(self):
        ret = ""
        num = len(self.children)
        if num == 0:
            ret += str(self.value)
        elif num == 1:
            ret += "({} )".format(self.operator, str(self.children[0]))
    
        elif num == 2:
            ret += "({} {} {})".format(str(self.children[0]), self.operator, str(self.children[1]))
    
        else:
            ret += "~" 
    
        return ret






