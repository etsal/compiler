class DanaType(object):
    base_types = [      \
        "byte", "int",  \
        # Internal datatypes
        "void", \
        "label",
    ]   
 
    # base is the argument giving the base type
    # From it, we can construct new types by either
    # turning it into a reference, or by turning it
    # into an array of set size
    def __init__(self, base, dims = [], ops = [], ref = False):
        if base not in self.base_types:
            raise ValueError("Base type {} invalid".format(base)) 
        if base in ["logic", "void"] and dims !=  []:
            raise ValueError("Danatype {} cannot have dimensions {}".format(base, dims))
            

        self.base = base
        self.dims = dims 
        self.ops = ops
        self.ref = ref

    def __str__(self):
        if self.base is not None:
            result = self.base
        else:
            result = "???"
        for dim in self.dims:
            result += "[{}]".format(dim) if dim > 0 else "[]" 
        for operand in self.ops:
            result += " (Arg: {})".format(operand) 
        return result 

    def __eq__(self, other_type):
        return self.base == other_type.base and len(self.dims) == len(other_type.dims) and self.ops == other_type.ops

    def __ne__(self, other_type):
        return not self.__eq__(other_type)            
    
