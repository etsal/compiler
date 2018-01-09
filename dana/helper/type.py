class DanaType(object):
    base_types = [      
        "byte", "int",  
        "void", 
        # Internal datatypes
        "logic",
        "label", 
        "invalid", 
    ]   
 
    # base is the argument giving the base type
    # From it, we can construct new types by either
    # turning it into a reference, or by turning it
    # into an array of set size
    def __init__(self, base, dims = [], args = [], ref = False):
        if base not in self.base_types:
            raise ValueError("Base type {} invalid".format(base)) 
        if base in ["logic", "void"] and dims !=  []:
            raise ValueError("Danatype {} cannot have dimensions {}".format(base, dims))
            
        object.__setattr__(self, "base", base)
        object.__setattr__(self, "dims", dims)
        object.__setattr__(self, "args", args)
        object.__setattr__(self, "ref", ref)


    def __setattr__(self, name, value):
            raise ValueError("Changing an immutable object")

    def __str__(self):
        result = self.base
        for dim in self.dims:
            result += "[{}]".format(dim) if dim > 0 else "[]" 
        if self.args:
            result += "({})".format(", ".join(map(str, self.args))) 
        return result 

    def __eq__(self, other):
        return self.base == other.base and len(self.dims) == len(other.dims) and self.args == other.args

    def __ne__(self, other):
        return not self.__eq__(other)            
    
