from collections import deque as deque
from helper.extendleft import extendleft_no_reverse as extendleft_no_reverse

class Node(object):
 
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.children = deque() 
        for child in args:
            self.children.append(child)
        self.value = kwargs.get("value", None)
        self.linespan = kwargs.get("linespan", (0,0))

    def __str__(self):
        result = self.name
        if self.value is not None:
            result += ", Value:{}".format(self.value)
        for child in self.children:
                 result += "\n" + "\n|".join(str(child).split('\n'))
        return result 

    def __eq__(self, other):
        return self.name == other.name and len(self.children) == len(other.children) \
                and all([child == otherchild for (child, otherchild) in zip(self.children, other.children)]) 


    def find_first_child(self, name):
        return self.find_first(name, only_children = True)

    def find_first(self, name, only_children = False):
        unprocessed = deque(self.children)
        while unprocessed:
            child = unprocessed.popleft()
    
            if isinstance(child, str):
                continue        
    
            elif child.name == name:                
                return child
     
            elif not only_children:
               extendleft_no_reverse(unprocessed, child.children)
    

    def find_all_children(self, name):
        return self.find_all(name, only_children = True)

    def find_all(self, name, only_children = False):
        subtrees = []
        unprocessed = deque(self.children)
        while unprocessed:
            child = unprocessed.popleft()
    
            if isinstance(child, str):
                continue        
    
            elif child.name == name:                
                subtrees.append(child)
     
            elif not only_children:
               extendleft_no_reverse(unprocessed, child.children)
    
        return subtrees

    def multifind_children(self, names):
        return self.multifind(names, only_children = True)

    def multifind(self, names, only_children = False): 
        subtrees = [] 
        unprocessed = deque(self.children)
        while unprocessed:
            child = unprocessed.popleft()
    
            if isinstance(child, str):
                continue        
    
            elif child.name in names:                
                subtrees.append(child)
     
            elif not only_children:
               extendleft_no_reverse(unprocessed, child.children)
    
        return subtrees

