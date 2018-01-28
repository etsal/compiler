	.text
	.file	"bsort.imm"
	.globl	main
	.align	16, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# BB#0:                                 # %.7
	pushq	%rbx
.Ltmp0:
	.cfi_def_cfa_offset 16
	subq	$80, %rsp
.Ltmp1:
	.cfi_def_cfa_offset 96
.Ltmp2:
	.cfi_offset %rbx, -16
	movl	$65, 76(%rsp)
	movl	$0, 72(%rsp)
	jmp	.LBB0_1
	.align	16, 0x90
.LBB0_2:                                # %.15
                                        #   in Loop: Header=BB0_1 Depth=1
	imull	$137, 76(%rsp), %eax
	movl	72(%rsp), %ecx
	leal	220(%rax,%rcx), %eax
	cltq
	imulq	$680390859, %rax, %rcx  # imm = 0x288DF0CB
	movq	%rcx, %rdx
	shrq	$63, %rdx
	sarq	$36, %rcx
	addl	%edx, %ecx
	imull	$101, %ecx, %ecx
	subl	%ecx, %eax
	movl	%eax, 76(%rsp)
	movslq	72(%rsp), %rcx
	movl	%eax, 8(%rsp,%rcx,4)
	incl	72(%rsp)
.LBB0_1:                                # %.11
                                        # =>This Inner Loop Header: Depth=1
	cmpl	$15, 72(%rsp)
	jle	.LBB0_2
# BB#3:                                 # %exit
	leaq	8(%rsp), %rbx
	movl	$str2, %edi
	movl	$16, %esi
	movq	%rbx, %rdx
	callq	main$writeArray
	movl	$16, %edi
	movq	%rbx, %rsi
	callq	main$bsort
	movl	$str3, %edi
	movl	$16, %esi
	movq	%rbx, %rdx
	callq	main$writeArray
	xorl	%edi, %edi
	callq	exit
	addq	$80, %rsp
	popq	%rbx
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc

	.globl	main$bsort
	.align	16, 0x90
	.type	main$bsort,@function
main$bsort:                             # @"main$bsort"
	.cfi_startproc
# BB#0:                                 # %entry
	pushq	%rbx
.Ltmp3:
	.cfi_def_cfa_offset 16
	subq	$16, %rsp
.Ltmp4:
	.cfi_def_cfa_offset 32
.Ltmp5:
	.cfi_offset %rbx, -16
	movq	%rsi, %rbx
	movl	%edi, 4(%rsp)
	.align	16, 0x90
.LBB1_1:                                # %.9
                                        # =>This Loop Header: Depth=1
                                        #     Child Loop BB1_2 Depth 2
	movb	$0, 15(%rsp)
	movl	$0, 8(%rsp)
	jmp	.LBB1_2
	.align	16, 0x90
.LBB1_5:                                # %.43
                                        #   in Loop: Header=BB1_2 Depth=2
	incl	8(%rsp)
.LBB1_2:                                # %.13
                                        #   Parent Loop BB1_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movl	4(%rsp), %eax
	decl	%eax
	cmpl	%eax, 8(%rsp)
	jge	.LBB1_6
# BB#3:                                 # %.19
                                        #   in Loop: Header=BB1_2 Depth=2
	movslq	8(%rsp), %rax
	movl	(%rbx,%rax,4), %ecx
	leal	1(%rax), %eax
	cltq
	cmpl	(%rbx,%rax,4), %ecx
	jle	.LBB1_5
# BB#4:                                 # %.29
                                        #   in Loop: Header=BB1_2 Depth=2
	movslq	8(%rsp), %rax
	leaq	(%rbx,%rax,4), %rdi
	leal	1(%rax), %eax
	cltq
	leaq	(%rbx,%rax,4), %rsi
	callq	main$bsort$swap
	movb	$1, 15(%rsp)
	jmp	.LBB1_5
	.align	16, 0x90
.LBB1_6:                                # %.55
                                        #   in Loop: Header=BB1_1 Depth=1
	movzbl	15(%rsp), %eax
	cmpl	$1, %eax
	je	.LBB1_1
# BB#7:                                 # %exit
	addq	$16, %rsp
	popq	%rbx
	retq
.Lfunc_end1:
	.size	main$bsort, .Lfunc_end1-main$bsort
	.cfi_endproc

	.globl	main$bsort$swap
	.align	16, 0x90
	.type	main$bsort$swap,@function
main$bsort$swap:                        # @"main$bsort$swap"
	.cfi_startproc
# BB#0:                                 # %entry
	movl	(%rdi), %eax
	movl	%eax, -4(%rsp)
	movl	(%rsi), %eax
	movl	%eax, (%rdi)
	movl	-4(%rsp), %eax
	movl	%eax, (%rsi)
	retq
.Lfunc_end2:
	.size	main$bsort$swap, .Lfunc_end2-main$bsort$swap
	.cfi_endproc

	.globl	main$writeArray
	.align	16, 0x90
	.type	main$writeArray,@function
main$writeArray:                        # @"main$writeArray"
	.cfi_startproc
# BB#0:                                 # %.9
	pushq	%rbx
.Ltmp6:
	.cfi_def_cfa_offset 16
	subq	$16, %rsp
.Ltmp7:
	.cfi_def_cfa_offset 32
.Ltmp8:
	.cfi_offset %rbx, -16
	movq	%rdx, %rbx
	movl	%esi, 8(%rsp)
	callq	writeString
	movl	$0, 12(%rsp)
	jmp	.LBB3_1
	.align	16, 0x90
.LBB3_4:                                # %.30
                                        #   in Loop: Header=BB3_1 Depth=1
	movslq	12(%rsp), %rax
	movl	(%rbx,%rax,4), %edi
	callq	writeInteger
	incl	12(%rsp)
.LBB3_1:                                # %.14
                                        # =>This Inner Loop Header: Depth=1
	movl	12(%rsp), %eax
	cmpl	8(%rsp), %eax
	jge	.LBB3_5
# BB#2:                                 # %.19
                                        #   in Loop: Header=BB3_1 Depth=1
	cmpl	$0, 12(%rsp)
	jle	.LBB3_4
# BB#3:                                 # %.23
                                        #   in Loop: Header=BB3_1 Depth=1
	movl	$str0, %edi
	callq	writeString
	jmp	.LBB3_4
.LBB3_5:                                # %exit
	movl	$str1, %edi
	callq	writeString
	addq	$16, %rsp
	popq	%rbx
	retq
.Lfunc_end3:
	.size	main$writeArray, .Lfunc_end3-main$writeArray
	.cfi_endproc

	.type	str0,@object            # @str0
	.section	.rodata.str1.1,"aMS",@progbits,1
	.globl	str0
str0:
	.asciz	", "
	.size	str0, 3

	.type	str1,@object            # @str1
	.globl	str1
str1:
	.asciz	"\n"
	.size	str1, 2

	.type	str2,@object            # @str2
	.globl	str2
str2:
	.asciz	"Initial array: "
	.size	str2, 16

	.type	str3,@object            # @str3
	.globl	str3
str3:
	.asciz	"Sorted array: "
	.size	str3, 15


	.section	".note.GNU-stack","",@progbits
