class Node:
 
    def __init__(self, name, *args):
        self.name = name
        self.children = [] 
        for child in args:
            self.children.append(child)
    def __str__(self):
        result = self.name
        for child in self.children:
                 result += "\n" + "\n|".join(str(child).split('\n'))
        return result

    def add(self, child):
        self.children.append(child)

    def remove(self):
        return self.children.pop(0)

