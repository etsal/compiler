from tree import * 

print("Base case")
n = Node("node",  Node("node2", Node("node3")), Node("node2"))
print(str(n))


print("Adding a child - always to the end")
n.children[0].children[0].add(Node("new"))
print (n)

print("Removing a child")
print(n.remove())
print (n)

print("Different way of passing a children list")
print(Node("list", *[n, Node("list2")]))

