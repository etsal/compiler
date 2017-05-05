from collections import deque as deque

class Node(object):
 
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.children = deque() 
        for child in args:
            self.children.append(child)
        self.value = kwargs.get("value", None)

    def __str__(self):
        result = self.name
        if self.value is not None:
            result += ", Value:{}".format(self.value)
        for child in self.children:
                 result += "\n" + "\n|".join(str(child).split('\n'))
        return result 

