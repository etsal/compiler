from compiler.codegen.type import irtype
from llvmlite import ir


def irgen_string(string, builder, table):
    """
    Return a string, creating it if does not exist yet. 
    """
    if not string.value in table.strings:
        string_type = irtype(string.type.base, dims=string.type.dims) 
        addr = ir.GlobalVariable(builder.module, string_type, table.gtable.new_name())

        addr.global_constant = True 
        addr.unnamed_addr = True

        encoded = bytearray(string.value.encode("ascii"))
        addr.initializer = ir.Constant(string_type, encoded)
        table.strings[string.value] = addr


    addr = table.strings[string.value]
    return builder.bitcast(addr, irtype("byte", pdepth=1))



def irgen_expr(expr, builder, table):
    """
    Generate a code sequence producing a Dana expression
    """
    operator = expr.operator
    special = dict({"const" : irgen_const,
                    "call" : irgen_func,
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
    return ir.Constant(irtype(expr.type.base), int(expr.value))    


def irgen_func(expr, builder, table):
    """
    Generate a code sequence producing a Dana func 
    """
    args = [irgen_expr(arg, builder, table) for arg in expr.children] 
    return irgen_call(builder, expr.value, args, table)


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
    return irgen_expr(expr.children[0], builder, table)




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
    logical negation 
    """
    return builder.not_(operand) 

def irgen_not(builder, operand):
    """
    Generate a code sequence producing the result of a 
    negation of a "truthy" or "falsey" value
    """
    byte_one = ir.Constant(irtype("byte"), 0x1)
    last_byte = builder.and_(byte_one, operand)
    return builder.sub(byte_one, operand)




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


# Since assignments can only be done on base types,
# we always return a pointer to a base type
def irgen_lvalue(lvalue, builder, table):
    """
    Generate an address of an lvalue 
    """
    addr = table[lvalue.value]
    val = addr
    if lvalue.children:
        exprs = [irgen_expr(child, builder, table) for child in lvalue.children]
        for expr in exprs[:-1]:
            val = builder.gep(addr, [expr])
            addr = builder.load(val)
        val = builder.gep(addr, [exprs[-1]])
              
    return val 

def irgen_call(builder, name, args, table):
    mangled = table.mangles[name]
    irfunction = table.gtable.funcs[mangled]
    func = irfunction.func
    extra = irfunction.args
    # Extra args are ref, so we pass an address
    args += [table[arg] for arg in extra]
    # Hack used because of the way we represent arrays
    # If we saved the array addresses and made array variables
    # mutable, we wouldn't need it
    for n, expected in enumerate(func.args):
        if expected.type == ir.PointerType(args[n].type):
           args[n] = args[n].operands[0] 
    return builder.call(func, args)
