import ast
from itertools import zip_longest as zip_longest
from compiler.semantic.type import DanaType as DanaType
from compiler.semantic.error import *

class DanaExpr(object):
    def __init__(self):
        self._set_attributes([], DanaType("invalid"), None)

    @classmethod
    def factory(self, d_expr, table):

        # Because the parsing rule is cond : expr | xcond,
        # we get the child and work we that instead
        if d_expr.name == "p_cond":
            d_expr = d_expr.children[0]

        const = d_expr.multifind_children(["p_number", "p_char", "p_boolean"])
        if const:
            return DanaConst(const[0])

        d_func_call = d_expr.find_first_child("p_func_call")
        if d_func_call:
            return DanaCall(d_func_call, table)

        # Lvalues are also represented by DanaExpr, so
        # because of the rule stmt : lvalue ":=" expr, 
        # d_expr might not actually be an expr
        d_lvalue = d_expr.find_first_child("p_lvalue")
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

        d_exprs = d_func_call.find_all("p_expr")
        exprs = [DanaExpr.factory(d_expr, table) for d_expr in d_exprs]
        types = [expr.type for expr in exprs]

        check_scope(d_func_call.linespan, name, table)
        base = table[name].base
        dtype = DanaType(base, args=types)
        dtype.check_type(d_func_call.linespan, table[name])

        dtype_base = DanaType(base)
        self._set_attributes(exprs, dtype_base, "call", value=name)


class DanaUnary(DanaExpr):
    def __init__(self, operator, operand, table):
        optype = dict({"!" : [DanaType("byte")], 
                      "+" : [DanaType("int")],
                      "-" : [DanaType("int")],
                      "not" : [DanaType("logic"), DanaType("byte")],
                     })
        renamed = dict({"!" : "!", 
                      "+" : "id",
                      "(" : "id" ,
                      "-" : "neg",
                      "not" : "not",
                     })


        super().__init__()
        child = DanaExpr.factory(operand, table)
        if operator in optype:
            child.type.in_types(operand.linespan, optype[operator])

        self._set_attributes([child], child.type, renamed[operator])
        return


class DanaBinary(DanaExpr):
    arithmetic_ops = ["+", "-", "*", "/", "%"]
    bit_ops = ["&", "|"]
    comparison_ops = ["==", "!=", "<", "<=", ">=", ">"]
    logic_ops = ["and", "or"]

    binary_ops = arithmetic_ops + bit_ops + \
                 comparison_ops + logic_ops

    def __init__(self, operator, arg1, arg2, table):
        renamed = dict({"STAR" : "*", 
                        "SLASH" : "/", 
                        "PERCENT" : "%", 
                        "=" : "==",
                      })

        super().__init__()
        op1 = DanaExpr.factory(arg1, table)
        op2 = DanaExpr.factory(arg2, table)
        optype = op2.type
        optype.check_type(arg1.linespan, op1.type)

        if operator in self.binary_ops + self.comparison_ops: 
            optype.in_types(arg1.linespan, [DanaType("int"), DanaType("byte")])

        if operator in self.bit_ops: 
            optype.check_type(arg1.linespan, DanaType("byte"))

        if operator in self.logic_ops: 
            logic_types = [DanaType("byte"), DanaType("logic"), DanaType("int")]
            optype.check_type(arg1.linespan, logic_types)

        operator = renamed[operator] if operator in renamed else operator
        self._set_attributes([op1, op2], op1.type, operator)



class DanaLvalue(DanaExpr):
    def __init__(self, d_lvalue, table):
        super().__init__()

        # The string case is self-contained
        string = d_lvalue.find_first_child("p_string")
        if string:
            value = ast.literal_eval(string.value) + "\0"
            dtype = DanaType("byte", dims=[len(value)])
            self._set_attributes([], dtype, "string", value)
            return


        # The function symbol
        d_id = d_lvalue.find_first("p_name")
        name = d_id.value
        check_scope(d_lvalue.linespan, name, table)

        # Get all indices
        d_exprs = d_lvalue.find_all("p_expr")
        exprs = [DanaExpr.factory(d_expr, table) for d_expr in d_exprs]
        for expr in exprs:
            expr.type.check_type(d_lvalue.linespan, DanaType("int")) 
                    
        # Make sure there are not too many indices
        base = table[name]
        total_dims = len(base.dims) + base.pdepth
        if total_dims < len(exprs):
            raise DanaTypeError("Invalid dereferencing")

        # When we have both dimensions and pdepth, we have 
        # a pointer to an array, not an array of pointers. 
        # That influences the type of the dereferenced expression
        dims, pdepth = (base.dims, base.pdepth)
        if len(exprs) > base.pdepth:
            dims = base.dims[(len(exprs) - base.pdepth):]
            pdepth = 0 
        else:
            dims = base.dims
            pdepth = base.pdepth - len(exprs)

        dtype = DanaType(base.base, \
                         dims=dims, \
                         pdepth=pdepth, \
                         args=base.args)
        
        self._set_attributes(exprs, dtype, "lvalue", value=name)
