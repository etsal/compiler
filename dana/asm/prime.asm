	.text
	.file	"prime.imm"
	.globl	main
	.align	16, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# BB#0:                                 # %.15
	subq	$24, %rsp
.Ltmp0:
	.cfi_def_cfa_offset 32
	movl	$str0, %edi
	callq	writeString
	callq	readInteger
	movl	%eax, 20(%rsp)
	movl	$str1, %edi
	callq	writeString
	movl	$0, 12(%rsp)
	cmpl	$2, 20(%rsp)
	jl	.LBB0_2
# BB#1:                                 # %.19
	incl	12(%rsp)
	movl	$2, %edi
	callq	writeInteger
	movl	$str2, %edi
	callq	writeString
.LBB0_2:                                # %.31
	cmpl	$3, 20(%rsp)
	jl	.LBB0_4
# BB#3:                                 # %.35
	incl	12(%rsp)
	movl	$3, %edi
	callq	writeInteger
	movl	$str2, %edi
	callq	writeString
.LBB0_4:                                # %.48
	movl	$5, 16(%rsp)
	jmp	.LBB0_5
	.align	16, 0x90
.LBB0_12:                               # %.121
                                        #   in Loop: Header=BB0_6 Depth=2
	addl	$4, 16(%rsp)
.LBB0_6:                                # %.63
                                        #   Parent Loop BB0_5 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movl	16(%rsp), %eax
	cmpl	20(%rsp), %eax
	jg	.LBB0_5
# BB#7:                                 # %.70
                                        #   in Loop: Header=BB0_6 Depth=2
	movl	16(%rsp), %edi
	callq	main$prime
	testb	%al, %al
	je	.LBB0_9
# BB#8:                                 # %.75
                                        #   in Loop: Header=BB0_6 Depth=2
	incl	12(%rsp)
	movl	16(%rsp), %edi
	callq	writeInteger
	movl	$str2, %edi
	callq	writeString
.LBB0_9:                                # %.95
                                        #   in Loop: Header=BB0_6 Depth=2
	movl	16(%rsp), %eax
	addl	$2, %eax
	movl	%eax, 16(%rsp)
	cmpl	20(%rsp), %eax
	jg	.LBB0_5
# BB#10:                                # %.102
                                        #   in Loop: Header=BB0_6 Depth=2
	movl	16(%rsp), %edi
	callq	main$prime
	testb	%al, %al
	je	.LBB0_12
# BB#11:                                # %.107
                                        #   in Loop: Header=BB0_6 Depth=2
	incl	12(%rsp)
	movl	16(%rsp), %edi
	callq	writeInteger
	movl	$str2, %edi
	callq	writeString
	jmp	.LBB0_12
	.align	16, 0x90
.LBB0_5:                                # %.53
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB0_6 Depth 2
	movl	16(%rsp), %eax
	cmpl	20(%rsp), %eax
	jle	.LBB0_6
# BB#13:                                # %exit
	movl	$str3, %edi
	callq	writeString
	movl	12(%rsp), %edi
	callq	writeInteger
	movl	$str2, %edi
	callq	writeString
	xorl	%edi, %edi
	callq	exit
	addq	$24, %rsp
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc

	.globl	main$prime
	.align	16, 0x90
	.type	main$prime,@function
main$prime:                             # @"main$prime"
	.cfi_startproc
# BB#0:                                 # %.7
	pushq	%rax
.Ltmp1:
	.cfi_def_cfa_offset 16
	movl	%edi, (%rsp)
	testl	%edi, %edi
	js	.LBB1_6
# BB#1:                                 # %.16
	movl	$3, 4(%rsp)
	jmp	.LBB1_2
	.align	16, 0x90
.LBB1_4:                                # %.39
                                        #   in Loop: Header=BB1_2 Depth=1
	addl	$2, 4(%rsp)
.LBB1_2:                                # %.19
                                        # =>This Inner Loop Header: Depth=1
	movl	(%rsp), %eax
	movl	%eax, %ecx
	shrl	$31, %ecx
	addl	%eax, %ecx
	sarl	%ecx
	cmpl	%ecx, 4(%rsp)
	jg	.LBB1_5
# BB#3:                                 # %.27
                                        #   in Loop: Header=BB1_2 Depth=1
	movl	(%rsp), %eax
	cltd
	idivl	4(%rsp)
	testl	%edx, %edx
	jne	.LBB1_4
# BB#7:                                 # %.33
	xorl	%eax, %eax
	popq	%rcx
	retq
.LBB1_6:                                # %.11
	movl	(%rsp), %edi
	negl	%edi
	callq	main$prime
	popq	%rcx
	retq
.LBB1_5:                                # %.47
	movb	$1, %al
	popq	%rcx
	retq
.Lfunc_end1:
	.size	main$prime, .Lfunc_end1-main$prime
	.cfi_endproc

	.type	str0,@object            # @str0
	.section	.rodata.str1.1,"aMS",@progbits,1
	.globl	str0
str0:
	.asciz	"Limit: "
	.size	str0, 8

	.type	str1,@object            # @str1
	.globl	str1
str1:
	.asciz	"Primes:\n"
	.size	str1, 9

	.type	str2,@object            # @str2
	.globl	str2
str2:
	.asciz	"\n"
	.size	str2, 2

	.type	str3,@object            # @str3
	.globl	str3
str3:
	.asciz	"Total: "
	.size	str3, 8


	.section	".note.GNU-stack","",@progbits
