from compiler.codegen.expr import *
from llvmlite import ir as ir

def irgen_stmt(stmt, builder, table):
    irgen = dict({"ret" : irgen_ret,
                  "continue" : irgen_continue,
                  "break" : irgen_break,
                  "call" : irgen_call,
                  "assign" : irgen_assign,
                })
    
    operator = stmt.operator
    irgen[operator](stmt, builder, table)


def irgen_ret(stmt, builder, table):
    if not stmt.exprs:
        builder.ret_void()
    else:
        builder.ret(irgen_expr(stmt.exprs[0], builder, table))

def irgen_continue(stmt, builder, table):
    tmp = builder.unreachable()             
    if stmt.label:
        table.conts[tmp] = (builder.block, table[stmt.label])
    else:
        table.conts[tmp] = (builder.block, None)

def irgen_break(stmt, builder, table):
    tmp = builder.unreachable()             
    if stmt.label:
        table.breaks[tmp] = (builder.block, table[stmt.label])
    else:
        table.breaks[tmp] = (builder.block, None) 

def irgen_call(stmt, builder, table):
    args = [irgen_expr(expr, builder, table) for expr in stmt.exprs]
    builder.call(table.funcs[stmt.value], args)


def irgen_assign(stmt, builder, table):
    lvalue = irgen_lvalue(stmt.exprs[0], builder, table)
    expr = irgen_expr(stmt.exprs[1], builder, table)
    builder.store(expr, lvalue)

