#!/bin/bash

if [ -z "$1" ]; 
then
	echo "No argument given"
	exit
fi

NAME="$1"

python -m compiler.codegen.codegen test/dana/"$NAME".dan > asm/"$NAME".imm
cd asm
llc "$NAME".imm -o "$NAME".asm
as "$NAME".asm -o "$NAME".o
ld "$NAME".o lib.a "/usr/lib/x86_64-linux-gnu/libc.a" -o "$NAME"
./"$NAME"

