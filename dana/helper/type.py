class DanaType(object):
    base_types = [      \
        "byte", "int",  \
        # Internal datatypes
        "logic", "void", \
    ]   
 
    # base is the argument giving the base type
    # From it, we can construct new types by either
    # turning it into a reference, or by turning it
    # into an array of set size
    def __init__(self, base, dimensions = [], ops = None, ref = False):
#        if base not in self.base_types:
#            raise ValueError("Base type {} invalid".format(base)) 
#        if base in ["logic", "void"] and dimensions !=  []:
#            raise ValueError("Danatype cannot have dimensions")

        self.base = base
        self.dimensions = dimensions 
        self.ops = ops
        self.ref = ref

    def __str__(self):
        result = self.base
        for ref in dimensions:
            result += "[{}]".format(ref) 
        if ops:
            for operand in ops:
                result += "\nArg:\t{}".format(operand) 
        return result 

    def __eq__(self, other_type):
        return self.base == other_type.base and self.dimensions == other_type.dimensions and self.ops == other_type.ops

            
    
