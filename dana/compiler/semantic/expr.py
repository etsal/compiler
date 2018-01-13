from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.symbol import Symbol as Symbol

class DanaExpr(object):

    unary_ops = ["neg", "!", "not"]

    arithmetic_ops= ["+", "-", "*", "/", "%"]
    bit_ops = ["&", "|"] 
    comparison_ops = [ "=", "!=", "<", "<=", ">=", ">"]
    logic_ops = ["and", "or"]  

    lvalue_ops = ["const", "id", "string", "lvalue"]  
    call_ops = ["call"]

    binary_ops = arithmetic_ops + bit_ops + \
                 comparison_ops + logic_ops
    operators = unary_ops + binary_ops + lvalue_ops + call_ops
                 

    def __init__(self, dana_expr, symbol_table):
        self._set_attributes([], DanaType("invalid"), None)
         

        # Because the parsing rule is cond : expr| xcond
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
        # Small hack: lvalues are also represented by DanaExpr, so
        # because of the rule stmt : lvalue ":=" expr dana_expr might
        # not actually be an expr
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
        
        
        
    def _make_const_expr(self, const): 
        value = const.value
        if const.value in ["true", "false"]:
            value = 1 if const.value == "true" else 0

        dtype = DanaType("int") if const.name == "p_number" else DanaType("byte") 
        self._set_attributes([], dtype, "const", value = value)
        return



    def _make_func_call(self, dana_func_call, symbol_table):
        name = dana_func_call.find_first_child("p_name").value
        if not name in symbol_table:
            print("Lines {}: Symbol {} not in scope".format(dana_func_call.linespan, name))
            return


        expected_args = symbol_table[name].args
        if expected_args is None:
            print("Lines {}: Nonfunction called as function", dana_func_call.linespan, name)
            return


        dana_exprs = dana_func_call.find_all("p_expr")
        exprs = [DanaExpr(dana_expr, symbol_table) for dana_expr in dana_exprs]
        types = [expr.type for expr in exprs]
        if expected_args != types:
            print("Lines {}: Arguments {} in function call {} instead of {} " \
                        .format(dana_func_call.linespan, \
                                [str(t) for t in types], name, [str(t) for t in expected_args]))
    

        dtype = DanaType(symbol_table[name].base)
        self._set_attributes([], dtype, "call", value = name)
        return



    def _make_unary(self, operator, operand, symbol_table):
        child = DanaExpr(operand, symbol_table)
        if operator in ["(", "+"]:
    
            if child.type != DanaType("int") and operator == "+":
                print("Lines {}: Operator {} for expression {}", operator, str(child.type)) 
                return 

            self._set_attributes([child], child.type, "id")
            return

        if (operator == "!" and child.type != DanaType("byte")) or \
           (operator == "-" and child.type != DanaType("int")) or \
           (operator == "not" and child.type != DanaType("logic")):
            print("Lines {}: Operator {} for expression {}", operator, str(child.type)) 

 
        operator = "neg" if operator == "-" else operator
        self._set_attributes([child], child.type, operator)
        return

    

    def _make_binary(self, operator, arg1, arg2, symbol_table): 
        op1 = DanaExpr(arg1, symbol_table) 
        op2 = DanaExpr(arg2, symbol_table) 
        if op1.type != op2.type:
            print("Lines {},{}: Operands {} and {}" \
                    .format(arg1.linespan, arg2.linespan, str(op1.type), str(op2.type))) 
            return

        # Map some operators to their symbols 
        new_names = dict({"STAR" : "*", "SLASH" : "/", "PERCENT" : "%"})
        if operator in new_names:
            operator = new_names[operator]


        if operator in self.binary_ops + self.comparison_ops and \
            not op1.type in [DanaType("int"), DanaType("byte")]:
            print("Lines {},{}: Operands {} for arithmetic operation" \
                    .format(arg1.linespan, arg2.linespan, str(self.type)))
            return

        if operator in self.bit_ops and op1.type != DanaType("byte"):
            print("Lines {},{}: Operands {} for byte operation" \
                    .format(arg1.linespan, arg2.linespan, str(self.type))) 
            return
 

        if operator in self.logic_ops and \
            not op1.type in [DanaType("logic"), DanaType("byte"), DanaType("int")]:

            print("Lines {},{}: Operands {} for logic operation" \
                    .format(arg1.linespan, arg2.linespan, str(self.type)))


        self.children += [op1, op2] 
        self.type = op1.type
        self.operator = new_names[operator] if operator in new_names else operator

        if not self.operator in self.operators:
            print("INVALID BINARY OPERATOR " + self.operator)


    # Possibilities: string, id, lvalue with index
    def _make_lvalue(self, dana_lvalue, symbol_table):

        string = dana_lvalue.find_first_child("p_string")
        if string:
            self.type = DanaType("byte", dims = [len(string.value) + 1])
            self.value = string.value + '\0'
            self.operator = "string"
            return


        name = dana_lvalue.find_first_child("p_name").value
        if name:
            if name not in symbol_table:
                print("Lines {}: Symbol {} not in scope".format(dana_lvalue.linespan, name))
                return

            self._set_attributes([], symbol_table[name], "lvalue", name)
            return

        
        dana_expr = stmt.find_first_child("p_expr")
        if dana_expr:

            expr = DanaExpr(dana_expr, symbol_table) 
            if expr.type != DanaType("int"):
                print("Lines {}: Type {} used as index"
                        .format(dana_lvalue.linespan, expr.type))
                return
    
            dana_lvalue_child = lvalue.find_first_child("p_lvalue")
            child = DanaExpr(dana_lvalue_child, symbol_table)
            if not child.type.dims:
                print("Lines {}: Base type {} dereferenced" \
                        .format(dana_lvalue_child.linespan, child.type))
                return
            

            dtype = DanaType(child.type.base, \
                                 dims = child.type.dims[1:], \
                                 args = child.type.ops)
            self._set_attributes([child], dtype, "lvalue")
            return



    def _set_attributes(self, children, dtype, operator, value = None):
            self.children = children
            self.type = dtype
            self.operator = operator
            self.value = None


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






