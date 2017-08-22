from helper.type import DanaType as DanaType 

builtins = [
    ("writeInteger", DanaType("void", ops = [DanaType("int")])), 
    ("writeByte", DanaType("void", ops = [DanaType("byte")])), 
    ("writeChar", DanaType("void", ops = [DanaType("byte")])),
    ("writeString", DanaType("void", ops = [DanaType("byte", [0])])), 
    ("readInteger", DanaType("int", ops = [DanaType("void")])), 
    ("readByte", DanaType("byte", ops = [DanaType("void")])), 
    ("readChar", DanaType("byte", ops = [DanaType("void")])), 
    ("readString", DanaType("byte", [0], ops = [DanaType("void")])),     
    ("strlen", DanaType("int", ops = [DanaType("byte", [0])])), 
    ("strcmp", DanaType("int", ops = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    ("strcat", DanaType("byte", [0], ops = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    ("strcpy", DanaType("byte", [0], ops = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    ("extend", DanaType("int", ops = [DanaType("byte")])), 
    ("shrink", DanaType( "byte", ops = [DanaType("int")])), 
    ("main", DanaType("void", ops = [DanaType("void")])),
]

