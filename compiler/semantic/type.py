class DanaType(object):
    """A type of the Dana language."""
    class DanaTypeError(Exception):
        pass

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
    def __init__(self, base, dims=[], args=None, is_ref=False, pdepth=0):
        if base not in self.base_types:
            raise self.DanaTypeError("Base type {} invalid".format(base))
        if base in ["logic", "void"] and dims != []:
            raise self.DanaTypeError("Danatype {} cannot have dimensions {}".format(base, dims))

        self.base = base
        self.dims = dims
        self.args = args
        self.is_ref = is_ref
        self.pdepth = pdepth

    def is_function(self):
        """Test whether the type is a function type.
           Note that args being None and being [] are
           two different things - None denotes non-functions,
           [] denotes a function that takes no arguments.
        """
        return self.args is not None

    def check_type(self, line, expected):
        if self != expected:
            raise self.DanaTypeError("L {}: Expected {}, got {}".format(line, expected, self))

    def in_types(self, line, expected):
        if not self in expected:
            raise self.DanaTypeError("L {}: Expected one of {}, got {}".format(line, str(expected), self))

    @property
    def is_pointer(self):
        return self.pdepth > 0

    @property
    def is_array(self):
        return len(self.dims) > 0

    def __str__(self):
        result = self.base
        if self.is_ref:
            result = "ref " + result
        result += "[]" * self.pdepth
        for dim in self.dims:
            result += "[{}]".format(dim)
        if self.args is not None:
            result += "({})".format(", ".join(map(str, self.args)))
        return result

    # The comparison between the dims depends on the spec of the language,
    # not sure whether the length of arrays matters - if it did, we would
    # be severely constrained when using them as arguments
    def __eq__(self, other):
        return self.base == other.base and \
               self.pdepth + len(self.dims) == other.pdepth + len(other.dims)and \
               self.args == other.args

    def __ne__(self, other):
        return not self.__eq__(other)
