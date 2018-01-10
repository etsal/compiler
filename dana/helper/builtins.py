from helper.type import DanaType as DanaType 
from helper.repr import Symbol as Symbol

builtins = [
    Symbol("writeInteger", DanaType("void", args = [DanaType("int")])), 
    Symbol("writeByte", DanaType("void", args = [DanaType("byte")])), 
    Symbol("writeChar", DanaType("void", args = [DanaType("byte")])),
    Symbol("writeString", DanaType("void", args = [DanaType("byte", [0])])), 
    Symbol("readInteger", DanaType("int", args = [DanaType("void")])), 
    Symbol("readByte", DanaType("byte", args = [DanaType("void")])), 
    Symbol("readChar", DanaType("byte", args = [DanaType("void")])), 
    Symbol("readString", DanaType("byte", [0], args = [DanaType("void")])),     
    Symbol("strlen", DanaType("int", args = [DanaType("byte", [0])])), 
    Symbol("strcmp", DanaType("int", args = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    Symbol("strcat", DanaType("byte", [0], args = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    Symbol("strcpy", DanaType("byte", [0], args = [DanaType("byte", [0]), DanaType("byte", [0])])), 
    Symbol("extend", DanaType("int", args = [DanaType("byte")])), 
    Symbol("shrink", DanaType( "byte", args = [DanaType("int")])), 
    Symbol("main", DanaType("void", args = [DanaType("void")])),
]

