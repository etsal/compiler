from helper.type import DanaType as DanaType 

builtins = [
    ("writeInteger", DanaType("void", args = [DanaType("int")])), 
    ("writeByte", DanaType("void", args = [DanaType("byte")])), 
    ("writeChar", DanaType("void", args = [DanaType("byte")])),
    ("writeString", DanaType("void", args = [DanaType("byte", [0])])), 
    ("readInteger", DanaType("int", args = [DanaType("void")])), 
    ("readByte", DanaType("byte", args = [DanaType("void")])), 
    ("readChar", DanaType("byte", args = [DanaType("void")])), 
    ("readString", DanaType("byte", [0], args = [DanaType("void")])),     
    ("strlen", DanaType("int", args = [DanaType("byte", [0])])), 
    ("strcmp", DanaType("int", args = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    ("strcat", DanaType("byte", [0], args = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    ("strcpy", DanaType("byte", [0], args = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    ("extend", DanaType("int", args = [DanaType("byte")])), 
    ("shrink", DanaType( "byte", args = [DanaType("int")])), 
    ("main", DanaType("void", args = [DanaType("void")])),
]

