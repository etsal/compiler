from llvmlite import ir as ir

def irbase(base):
    ir_base = dict({"int"   : ir.IntType(32),
                    "byte"  : ir.IntType(8),
                    "logic" : ir.IntType(1),
                    "void"  : ir.VoidType(),
                    "label" : ir.LabelType(),
                    })
    return ir_base[base]

def irtype(base, pdepth=0, dims=[]):
    """
    Produce an LLVM IR Type from a DanaType 
    The no_arrays flag results in the creation of 
    pointer types instead of array types, which
    are useful only for stack allocations.
    """
    t = irbase(base)

    for _ in range(pdepth):
        t = ir.PointerType(t)

    for dim in dims:
        t = ir.ArrayType(t, dim)

    return t
    
        
