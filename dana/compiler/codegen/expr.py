from llvmlite import ir as ir

# no_arrays????
def irtype(dana_type, no_arrays = False):
    ir_base = dict({"int"   : ir.IntType(32),
                    "byte"  : ir.IntType(8),
                    "logic" : ir.IntType(1),
                    "void"  : ir.VoidType(),
                    "label" : ir.LabelType(),
                    })
    t = ir_base[dana_type.base]
    
    # We choose whether to produce an array type or a pointer type
    for num in dana_type.dims:
        if num and not no_arrays:
            t = ir.ArrayType(t, num)
        else:
            t = ir.PointerType(t)

    if dana_type.args is not None:
        t = ir.FunctionType(t, [irtype(arg) for arg in dana_type.args])
        
    return t

# Multidimensional arrays?
def irpointer(addr, dana_type, builder):
    if dana_type.dims and any(x for x in dana_type.dims): 
        return builder.bitcast(addr, irtype(dana_type, no_arrays = True))
    else:
        return addr

def irgen_string(string, builder, table):
    if not string.value in table.globals:
        string_type = irtype(string.type) 
        addr = ir.GlobalVariable(builder.module, string_type, table.new_name())

        addr.global_constant = True 
        addr.unnamed_addr = True

        encoded = bytearray(string.value.encode("ascii"))
        addr.initializer = ir.Constant(string_type, encoded)
        table.globals[string.value] = addr

    else:
        addr = table.globals[string.value]

    return irpointer(addr, string.type, builder)



def irgen_expr(expr, builder, table):
    operator = expr.operator
    special = dict({"const" : irgen_const,
                    "call" : irgen_call,
                    "lvalue" : irgen_rvalue,
                    "string" : irgen_string,
                    "id" : irgen_id,
                   })

    if operator in special.keys():
        return special[operator](expr, builder, table)


    if len(expr.children) == 1:
        operand = irgen_expr(expr.children[0], builder, table)
        return irgen_unary(builder, operator, operand)

    else:
        first = irgen_expr(expr.children[0], builder, table)
        second = irgen_expr(expr.children[1], builder, table)
        return irgen_binary(builder, operator, first, second)


def irgen_const(expr, builder, table):
    return ir.Constant(irtype(expr.type), int(expr.value))    

def irgen_call(expr, builder, table):
    name = expr.value
    args = [irgen_expr(arg, builder, table) for arg in expr.children]
    return builder.call(table.funcs[name], args, name)

def irgen_rvalue(expr, builder, table):
    addr = irgen_lvalue(expr, builder, table)
    return builder.load(addr)

def irgen_id(expr, builder, table):
    return irgen_expr(operand, builder, table)




def irgen_unary(builder, operator, operand):
    operations = dict({"neg": irgen_neg,
                        "!": irgen_bang,
                        "not": irgen_not,})
    return operations[operator](builder, operand)


def irgen_neg(builder, operand):
    return builder.neg(operand)

def irgen_bang(builder, operand):
    byte_one = ir.Constant(irtype["byte"], 0x1)
    last_byte = builder.and_(byte_one, operand)
    return builder.sub(byte_one, operand)

def irgen_not(builder, operand):
    return builder.not_(operand) 




def irgen_binary(builder, operator, first, second):
    operations = dict({"+": builder.add,
                       "-": builder.sub,
                       "*": builder.mul,
                       "/": builder.sdiv,
                       "%": builder.srem,
                       "&": builder.and_,
                       "|": builder.or_,
                       "and": builder.and_, 
                       "or": builder.or_,
                       })

    comparisons = ["==", "!=", "<", "<=", ">=", ">",]

    if operator in comparisons:
        return builder.icmp_signed(operator, first, second)    
        
    return operations[operator](first, second)



def irgen_lvalue(lvalue, builder, table):
    addr = table[lvalue.value]
    if lvalue.children:
        exprs = [irgen_expr(child, builder, table) for child in lvalue.children]
        for expr in exprs:
            addr = builder.gep(addr, [expr])

    return addr

