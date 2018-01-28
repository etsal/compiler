	.text
	.file	"hanoi.imm"
	.globl	solve
	.align	16, 0x90
	.type	solve,@function
solve:                                  # @solve
	.cfi_startproc
# BB#0:                                 # %entry
	pushq	%rax
.Ltmp0:
	.cfi_def_cfa_offset 16
	movl	$str3, %edi
	callq	writeString
	callq	readInteger
	movl	%eax, 4(%rsp)
	movl	$str4, %esi
	movl	$str5, %edx
	movl	$str6, %ecx
	movl	%eax, %edi
	callq	solve$hanoi
	xorl	%edi, %edi
	callq	exit
	popq	%rax
	retq
.Lfunc_end0:
	.size	solve, .Lfunc_end0-solve
	.cfi_endproc

	.globl	solve$hanoi
	.align	16, 0x90
	.type	solve$hanoi,@function
solve$hanoi:                            # @"solve$hanoi"
	.cfi_startproc
# BB#0:                                 # %.9
	pushq	%r15
.Ltmp1:
	.cfi_def_cfa_offset 16
	pushq	%r14
.Ltmp2:
	.cfi_def_cfa_offset 24
	pushq	%rbx
.Ltmp3:
	.cfi_def_cfa_offset 32
	subq	$16, %rsp
.Ltmp4:
	.cfi_def_cfa_offset 48
.Ltmp5:
	.cfi_offset %rbx, -32
.Ltmp6:
	.cfi_offset %r14, -24
.Ltmp7:
	.cfi_offset %r15, -16
	movq	%rcx, %r15
	movq	%rdx, %r14
	movq	%rsi, %rbx
	movl	%edi, 12(%rsp)
	testl	%edi, %edi
	jle	.LBB1_2
# BB#1:                                 # %.13
	movl	12(%rsp), %edi
	decl	%edi
	movq	%rbx, %rsi
	movq	%r15, %rdx
	movq	%r14, %rcx
	callq	solve$hanoi
	movq	%rbx, %rdi
	movq	%r14, %rsi
	callq	solve$hanoi$move
	movl	12(%rsp), %edi
	decl	%edi
	movq	%r15, %rsi
	movq	%r14, %rdx
	movq	%rbx, %rcx
	callq	solve$hanoi
.LBB1_2:                                # %exit
	addq	$16, %rsp
	popq	%rbx
	popq	%r14
	popq	%r15
	retq
.Lfunc_end1:
	.size	solve$hanoi, .Lfunc_end1-solve$hanoi
	.cfi_endproc

	.globl	solve$hanoi$move
	.align	16, 0x90
	.type	solve$hanoi$move,@function
solve$hanoi$move:                       # @"solve$hanoi$move"
	.cfi_startproc
# BB#0:                                 # %entry
	pushq	%r14
.Ltmp8:
	.cfi_def_cfa_offset 16
	pushq	%rbx
.Ltmp9:
	.cfi_def_cfa_offset 24
	pushq	%rax
.Ltmp10:
	.cfi_def_cfa_offset 32
.Ltmp11:
	.cfi_offset %rbx, -24
.Ltmp12:
	.cfi_offset %r14, -16
	movq	%rsi, %r14
	movq	%rdi, %rbx
	movl	$str0, %edi
	callq	writeString
	movq	%rbx, %rdi
	callq	writeString
	movl	$str1, %edi
	callq	writeString
	movq	%r14, %rdi
	callq	writeString
	movl	$str2, %edi
	callq	writeString
	addq	$8, %rsp
	popq	%rbx
	popq	%r14
	retq
.Lfunc_end2:
	.size	solve$hanoi$move, .Lfunc_end2-solve$hanoi$move
	.cfi_endproc

	.type	str0,@object            # @str0
	.section	.rodata.str1.1,"aMS",@progbits,1
	.globl	str0
str0:
	.asciz	"Moving from "
	.size	str0, 13

	.type	str1,@object            # @str1
	.globl	str1
str1:
	.asciz	" to "
	.size	str1, 5

	.type	str2,@object            # @str2
	.globl	str2
str2:
	.asciz	".\n"
	.size	str2, 3

	.type	str3,@object            # @str3
	.globl	str3
str3:
	.asciz	"Rings: "
	.size	str3, 8

	.type	str4,@object            # @str4
	.globl	str4
str4:
	.asciz	"left"
	.size	str4, 5

	.type	str5,@object            # @str5
	.globl	str5
str5:
	.asciz	"right"
	.size	str5, 6

	.type	str6,@object            # @str6
	.globl	str6
str6:
	.asciz	"middle"
	.size	str6, 7


	.section	".note.GNU-stack","",@progbits
