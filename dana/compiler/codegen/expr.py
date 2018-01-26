from llvmlite import ir as ir

def irtype(dana_type, no_arrays = False):
    """
    Produce an LLVM IR Type from a DanaType 
    The no_arrays flag results in the creation of 
    pointer types instead of array types, which
    are useful only for stack allocations.
    """
    ir_base = dict({"int"   : ir.IntType(32),
                    "byte"  : ir.IntType(8),
                    "logic" : ir.IntType(1),
                    "void"  : ir.VoidType(),
                    "label" : ir.LabelType(),
                    })
    t = ir_base[dana_type.base]
    
    # Choose whether to produce an array type or a pointer type
    for num in dana_type.dims:
        if num and not no_arrays:
            t = ir.ArrayType(t, num)
        else:
            t = ir.PointerType(t)

    # If no_arrays is set, and we have a function, then every array type
    # gets passed by reference. Return values are always base types anyway.
    if dana_type.args is not None:
        t = ir.FunctionType(t, [irtype(arg, no_arrays=no_arrays) for arg in dana_type.args])
        
    return t


def irpointer(addr, dana_type, builder):
    """
    Get a pointer for a given address for an object of type DanaType.
    """
    if dana_type.dims and any(x for x in dana_type.dims): 
        return builder.bitcast(addr, irtype(dana_type, no_arrays = True))
    else:
        return addr


def irgen_string(string, builder, table):
    """
    Return a string, creating it if does not exist yet. 
    """
    if not string.value in table.globals:
        string_type = irtype(string.type) 
        addr = ir.GlobalVariable(builder.module, string_type, table.new_name())

        addr.global_constant = True 
        addr.unnamed_addr = True

        encoded = bytearray(string.value.encode("ascii"))
        addr.initializer = ir.Constant(string_type, encoded)
        table.globals[string.value] = addr


    addr = table.globals[string.value]
    return irpointer(addr, string.type, builder)



def irgen_expr(expr, builder, table):
    """
    Generate a code sequence producing a Dana expression
    """
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
    """
    Generate a code sequence producing a Dana constant 
    """
    return ir.Constant(irtype(expr.type), int(expr.value))    


def irgen_call(expr, builder, table):
    """
    Generate a code sequence producing a Dana call 
    """
    name = expr.value
    args = [irgen_expr(arg, builder, table) for arg in expr.children]
    
    # Extra arguments implementing static scoping
    mangled= table[name]
    args += [builder.load(mangled) for name in table.extra_args[mangled]]

    return builder.call(mangled, args, name)


def irgen_rvalue(expr, builder, table):
    """
    Generate a code sequence producing a Dana rvalue from an lvalue 
    """
    addr = irgen_lvalue(expr, builder, table)
    return builder.load(addr)


def irgen_id(expr, builder, table):
    """
    Generate a code sequence producing a Dana id operation 
    """
    return irgen_expr(operand, builder, table)




def irgen_unary(builder, operator, operand):
    """
    Generate a code sequence producing the result of a 
    unary operation
    """
    operations = dict({"neg": irgen_neg,
                        "!": irgen_bang,
                        "not": irgen_not,})
    return operations[operator](builder, operand)


def irgen_neg(builder, operand):
    """
    Generate a code sequence producing the result of an 
    arithmetic negation
    """
    return builder.neg(operand)

def irgen_bang(builder, operand):
    """
    Generate a code sequence producing the result of a 
    negation of a "truthy" or "falsey" value
    """
    byte_one = ir.Constant(irtype["byte"], 0x1)
    last_byte = builder.and_(byte_one, operand)
    return builder.sub(byte_one, operand)

def irgen_not(builder, operand):
    """
    Generate a code sequence producing the result of a 
    logical negation 
    """
    return builder.not_(operand) 




def irgen_binary(builder, operator, first, second):
    """
    Generate a code sequence producing the result of a 
    binary operation
    """
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



#BROKEN FOR MULTIDIMENSIONAL ARRAYS
def irgen_lvalue(lvalue, builder, table):
    """
    Generate an address of an lvalue 
    """
    addr = table[lvalue.value]
    if lvalue.children:
        exprs = [irgen_expr(child, builder, table) for child in lvalue.children]
        for expr in exprs:
            addr = builder.gep(addr, [expr])

    return addr

