from compiler.codegen.expr import irgen_expr, irgen_lvalue, irgen_call 
from llvmlite import ir

def irgen_stmt(stmt, builder, table):
    """
    Produce a Dana statement
    """
    irgen = dict({"ret" : irgen_ret,
                  "continue" : irgen_continue,
                  "break" : irgen_break,
                  "call" : irgen_proc,
                  "assign" : irgen_assign,
                  "skip" : irgen_skip,
                })
    
    operator = stmt.operator
    irgen[operator](stmt, builder, table)


def irgen_ret(stmt, builder, table):
    """
    Produce a ret statement
    """
    if not stmt.exprs:
        builder.ret_void()
    else:
        builder.ret(irgen_expr(stmt.exprs[0], builder, table))

def irgen_continue(stmt, builder, table):
    """
    Produce a continue statement - actually mark where it should
    be backpatched, at least
    """
    tmp = builder.unreachable()             
    if stmt.label:
        table.conts[tmp] = (builder.block, table[stmt.label])
    else:
        table.conts[tmp] = (builder.block, None)

def irgen_break(stmt, builder, table):
    """
    Produce a break statement - actually mark where it should
    be backpatched, at least
    """
    tmp = builder.unreachable()             
    if stmt.label:
        table.breaks[tmp] = (builder.block, table[stmt.label])
    else:
        table.breaks[tmp] = (builder.block, None) 

def irgen_proc(stmt, builder, table):
    """
    Produce a proc statement
    """
    args = [irgen_expr(expr, builder, table) for expr in stmt.exprs]

    # Extra arguments implementing static scoping
    return irgen_call(builder, stmt.value, args, table)


def irgen_assign(stmt, builder, table):
    """
    Produce an assign statement
    """
    lvalue = irgen_lvalue(stmt.exprs[0], builder, table)
    expr = irgen_expr(stmt.exprs[1], builder, table)
    builder.store(expr, lvalue)


def irgen_skip(stmt, builder, table):
    """
    Produce a skip statement
    """
    pass
