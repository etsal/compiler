class Symbol(object):
    def __init__(self, name, dana_type):
        self.name = name
        self.type = dana_type

    def __str__(self):
        return "({},{})".format(self.name, self.type)

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(self, other)
