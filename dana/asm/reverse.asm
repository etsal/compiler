	.text
	.file	"reverse.imm"
	.globl	main
	.align	16, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# BB#0:                                 # %exit
	pushq	%rbx
.Ltmp0:
	.cfi_def_cfa_offset 16
	subq	$32, %rsp
.Ltmp1:
	.cfi_def_cfa_offset 48
.Ltmp2:
	.cfi_offset %rbx, -16
	leaq	(%rsp), %rbx
	movl	$str0, %edi
	movq	%rbx, %rsi
	callq	main$reverse
	movq	%rbx, %rdi
	callq	writeString
	xorl	%edi, %edi
	callq	exit
	addq	$32, %rsp
	popq	%rbx
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc

	.globl	main$reverse
	.align	16, 0x90
	.type	main$reverse,@function
main$reverse:                           # @"main$reverse"
	.cfi_startproc
# BB#0:                                 # %.7
	pushq	%r14
.Ltmp3:
	.cfi_def_cfa_offset 16
	pushq	%rbx
.Ltmp4:
	.cfi_def_cfa_offset 24
	pushq	%rax
.Ltmp5:
	.cfi_def_cfa_offset 32
.Ltmp6:
	.cfi_offset %rbx, -24
.Ltmp7:
	.cfi_offset %r14, -16
	movq	%rsi, %r14
	movq	%rdi, %rbx
	callq	strlen
	movl	%eax, (%rsp)
	movl	$0, 4(%rsp)
	jmp	.LBB1_1
	.align	16, 0x90
.LBB1_2:                                # %.18
                                        #   in Loop: Header=BB1_1 Depth=1
	movslq	4(%rsp), %rax
	movl	(%rsp), %ecx
	subl	%eax, %ecx
	decl	%ecx
	movslq	%ecx, %rcx
	movb	(%rbx,%rcx), %cl
	movb	%cl, (%r14,%rax)
	incl	4(%rsp)
.LBB1_1:                                # %.13
                                        # =>This Inner Loop Header: Depth=1
	movl	4(%rsp), %eax
	cmpl	(%rsp), %eax
	jl	.LBB1_2
# BB#3:                                 # %exit
	movslq	4(%rsp), %rax
	movb	$0, (%r14,%rax)
	addq	$8, %rsp
	popq	%rbx
	popq	%r14
	retq
.Lfunc_end1:
	.size	main$reverse, .Lfunc_end1-main$reverse
	.cfi_endproc

	.type	str0,@object            # @str0
	.section	.rodata.str1.1,"aMS",@progbits,1
	.globl	str0
str0:
	.asciz	"\n!dlrow olleH"
	.size	str0, 14


	.section	".note.GNU-stack","",@progbits
