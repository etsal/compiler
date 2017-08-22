from collections import deque as deque
from copy import copy as copy

# Simple method for doing a preorder traversal 
# of the AST using a deque
def extendleft_no_reverse(main_deque, new_elems):
    new_elems_copy = new_elems.__copy__()
    new_elems_copy.reverse()
    main_deque.extendleft(new_elems_copy) 
