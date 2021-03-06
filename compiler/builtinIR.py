# Library code for the Dana Language
BUILTINS_IR = \
"""
target triple = "x86_64-linux-gnu"

declare i32 @printf(i8*, ...)
declare i32 @scanf(i8*, ...)

define i8 @readChar()
{
    %1 = alloca i8 
    %fmt = bitcast [3 x i8]* @.chr to i8*
    %2 = call i32 (i8*, ...) @scanf(i8* %fmt, i8* %1)
    %3 = load i8, i8* %1
    ret i8 %3
}

define i8 @readByte()
{
    %1 = alloca i8 
    %fmt = bitcast [3 x i8]* @.num to i8*
    %2 = call i32 (i8*, ...) @scanf(i8* %fmt, i8* %1)
    %3 = load i8, i8* %1
    ret i8 %3

}

define i32 @readInteger()
{
    %1 = alloca i32 
    %fmt = bitcast [3 x i8]* @.num to i8*
    %2 = call i32 (i8*, ...) @scanf(i8* %fmt, i32* %1)
    %3 = load i32, i32* %1
    ret i32 %3
}

define void @readString(i8* %str)
{
    %fmt = bitcast [3 x i8]* @.str to i8*
    %1 = call i32 (i8*, ...) @scanf(i8* %fmt, i8* %str)
    ret void
}

define void @writeChar(i8 %char)
{
    %fmt = bitcast [3 x i8]* @.chr to i8*
    %1 = call i32 (i8*, ...) @printf(i8* %fmt, i8 %char)
    ret void
}

define void @writeByte(i8 %byte)
{
    %fmt = bitcast [3 x i8]* @.num to i8*
    %1 = call i32 (i8*, ...) @printf(i8* %fmt, i8 %byte)
    ret void
}

define void @writeInteger(i32 %num)
{
    %fmt = bitcast [3 x i8]* @.num to i8*
    %1 = call i32 (i8*, ...) @printf(i8* %fmt, i32 %num)
    ret void
}

define void @writeString(i8* %str)
{
    %fmt = bitcast [3 x i8]* @.str to i8*
    %1 = call i32 (i8*, ...) @printf(i8* %fmt, i8* %str)
    ret void
}


define i32 @extend(i8 %byte)
{
    %1 = zext i8 %byte to i32
    ret i32 %1
}

define i8 @shrink(i32 %num)
{
    %1 = trunc i32 %num to i8
    ret i8 %1
}

@.str = constant [3 x i8] c"%s\00"
@.chr = constant [3 x i8] c"%c\00"
@.num = constant [3 x i8] c"%d\00"

"""
