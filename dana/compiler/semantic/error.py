class ScopeError(Exception):
    pass



def check_scope(line, name, table):
    if name not in table:
        raise ScopeError("L {}: Unknown symbol {}".format(line, name))

def check_table(line, symbol, table):
    check_scope(line, symbol.name, table)
    expected = table[symbol.name]
    symbol.type.check_type(line, expected)
