#!/bin/sh

set -euo

if [ -z "$1" ]; 
then
	echo "No argument given"
	exit
fi

NAME="$1"

python3 -m compiler.compiler compiler/tests/dana/"$NAME".dan > asm/"$NAME".imm
cd asm
# Compile the "standard library" of the language
llc "builtins.imm" -o "builtins.asm"
llc "$NAME".imm -o "$NAME".asm
clang "$NAME".asm builtins.asm -o "$NAME"

