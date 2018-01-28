class DanaTypeError(Exception):
    pass

class ScopeError(Exception):
    pass


def check_type(line, expected, actual):
    if actual != expected:
        raise DanaTypeError("L {}: Expected {}, got {}".format(line, expected, actual))

def check_scope(line, name, table):
    if name not in table:
        raise ScopeError("L {}: Unknown symbol {}".format(line, name))

def check_table(line, symbol, table):
    check_scope(line, symbol.name, table)
    expected = table[symbol.name]
    check_type(line, expected, symbol.type) 

def in_types(line, expected, actual):
    if not actual in expected:
        raise DanaTypeError("L {}: Expected one of {}, got {}".format(line, *expected, actual))
