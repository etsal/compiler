from itertools import zip_longest as zip_longest
from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.error import *

class DanaExpr(object):
    def __init__(self):
        self._set_attributes([], DanaType("invalid"), None)

    @classmethod
    def factory(self, d_expr, table):

        # Because the parsing rule is cond : expr | xcond
        if d_expr.name == "p_cond":
            d_expr = d_expr.children[0]

        const = d_expr.multifind_children(["p_number", "p_char", "p_boolean"])
        if const:
            return DanaConst(const[0])

        d_func_call = d_expr.find_first_child("p_func_call")
        if d_func_call:
            return DanaCall(d_func_call, table)

        d_lvalue = d_expr.find_first_child("p_lvalue")
        # Small hack: lvalues are also represented by DanaExpr, so
        # because of the rule stmt : lvalue ":=" expr d_expr might
        # not actually be an expr
        if d_expr.name == "p_lvalue":
            d_lvalue = d_expr

        if d_lvalue:
            return DanaLvalue(d_lvalue, table)

        args = d_expr.multifind(["p_expr", "p_cond"])
        if len(args) == 1:
            return DanaUnary(d_expr.children[0], args[0], table)

        elif len(args) == 2:
            return DanaBinary(d_expr.children[1], args[0], args[1], table)




    def _set_attributes(self, children, dtype, operator, value=None):
        self.children = children
        self.type = dtype
        self.operator = operator
        self.value = value


    def __str__(self):
        ret = ""
        num = len(self.children)
        if num == 0:
            ret += str(self.value)
        elif num == 1:
            ret += "({} {})".format(self.operator, str(self.children[0]))
        elif num == 2:
            ret += "({} {} {})".format(str(self.children[0]), self.operator, str(self.children[1]))
        else:
            ret += "~"
        return ret


class DanaConst(DanaExpr):
    def __init__(self, const):
        super().__init__()
        value = const.value
        if const.value in ["true", "false"]:
            value = 1 if const.value == "true" else 0

        dtype = DanaType("int") if const.name == "p_number" else DanaType("byte")
        self._set_attributes([], dtype, "const", value=value)


class DanaCall(DanaExpr):
    def __init__(self, d_func_call, table):
        super().__init__()
        name = d_func_call.find_first_child("p_name").value
        check_scope(d_func_call.linespan, name, table)

        if not table[name].is_function():
            print("Lines {}: Nonfunction called as function", d_func_call.linespan, name)
            raise DanaTypeError

        expected_args = table[name].args
        d_exprs = d_func_call.find_all("p_expr")
        exprs = [DanaExpr.factory(d_expr, table) for d_expr in d_exprs]
        types = [expr.type for expr in exprs]
        if expected_args != types:
            print("Lines {}: Arguments {} in function call {} instead of {} " \
                        .format(d_func_call.linespan, \
                                [str(t) for t in types], name, [str(t) for t in expected_args]))

        dtype = DanaType(table[name].base)
        self._set_attributes(exprs, dtype, "call", value=name)


class DanaUnary(DanaExpr):
    def __init__(self, operator, operand, table):
        super().__init__()
        child = DanaExpr.factory(operand, table)
        if operator == "(":
            self._set_attributes([child], child.type, "id")
            return

        if operator == "+":
            check_type(operand.linespan, child.type, DanaType("int"))
            self._set_attributes([child], child.type, "id")
            return

        if (operator == "!" and child.type != DanaType("byte")) or \
           (operator == "-" and child.type != DanaType("int")) or \
           (operator == "not" and child.type != DanaType("logic")):
            print("Lines {}: Operator {} for expression {}", operator, str(child.type))

        operator = "neg" if operator == "-" else operator
        self._set_attributes([child], child.type, operator)
        return


class DanaBinary(DanaExpr):
    arithmetic_ops = ["+", "-", "*", "/", "%"]
    bit_ops = ["&", "|"]
    comparison_ops = ["==", "!=", "<", "<=", ">=", ">"]
    logic_ops = ["and", "or"]

    binary_ops = arithmetic_ops + bit_ops + \
                 comparison_ops + logic_ops

    def __init__(self, operator, arg1, arg2, table):
        super().__init__()
        op1 = DanaExpr.factory(arg1, table)
        op2 = DanaExpr.factory(arg2, table)
        if op1.type != op2.type:
            print("Lines {},{}: Operands {} and {}" \
                    .format(arg1.linespan, arg2.linespan, str(op1.type), str(op2.type)))
            return

        # Map some operators to their symbols
        new_names = dict({"STAR" : "*", "SLASH" : "/", "PERCENT" : "%", "=" : "==",})


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




class DanaLvalue(DanaExpr):
    def __init__(self, d_lvalue, table):
        super().__init__()

        string = d_lvalue.find_first_child("p_string")
        if string:
            dtype = DanaType("byte", dims=[len(string.value) + 1])
            self._set_attributes([], dtype, "string", string.value + '\0')
            return


        d_id = d_lvalue.find_first("p_name")
        name = d_id.value
        check_scope(d_lvalue.linespan, name, table)

        d_exprs = d_lvalue.find_all("p_expr")
        exprs = [DanaExpr.factory(d_expr, table) for d_expr in d_exprs]
        for expr in exprs:
            check_type(d_lvalue.linespan, expr.type, DanaType("int")) 
                    
        base = table[name]
        if len(base.dims) < len(exprs):
            raise TypeError("Invalid dereferencing")

        dtype = DanaType(base.base, \
                         dims=base.dims[len(exprs):], \
                         args=base.args)
        
        self._set_attributes(exprs, dtype, "lvalue", value=name)
