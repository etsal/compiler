from compiler.semantic.error import *

class DanaType(object):
    """A type of the Dana language."""

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
    def __init__(self, base, dims=[], args=None, ref=False):
        if base not in self.base_types:
            raise DanaTypeError("Base type {} invalid".format(base))
        if base in ["logic", "void"] and dims != []:
            raise DanaTypeError("Danatype {} cannot have dimensions {}".format(base, dims))

        self.base = base
        self.dims = dims
        self.args = args
        self.ref = ref


    def is_function(self):
        """Test whether the type is a function type.
           Note that args being None and being [] are
           two different things - None denotes non-functions,
           [] denotes a function that takes no arguments.
        """
        return self.args is not None

    def is_reference(self):
        return self.ref

    

    def __str__(self):
        result = self.base
        for dim in self.dims:
            result += "[{}]".format(dim) if dim > 0 else "[]"
        if self.args is not None:
            result += "({})".format(", ".join(map(str, self.args)))
        return result

    def __eq__(self, other):
        return self.base == other.base and \
               len(self.dims) == len(other.dims) and \
               self.args == other.args

    def __ne__(self, other):
        return not self.__eq__(other)
