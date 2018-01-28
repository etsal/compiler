	.text
	.file	"digitfreq.imm"
	.globl	main
	.align	16, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# BB#0:                                 # %.9
	subq	$200, %rsp
.Ltmp0:
	.cfi_def_cfa_offset 208
	movl	$0, 4(%rsp)
	jmp	.LBB0_1
	.align	16, 0x90
.LBB0_2:                                # %.23
                                        #   in Loop: Header=BB0_1 Depth=1
	incl	4(%rsp)
.LBB0_1:                                # %.17
                                        # =>This Inner Loop Header: Depth=1
	movslq	4(%rsp), %rax
	movl	$0, 164(%rsp,%rax,4)
	cmpl	$9, 4(%rsp)
	jne	.LBB0_2
	jmp	.LBB0_3
	.align	16, 0x90
.LBB0_4:                                # %.46
                                        #   in Loop: Header=BB0_3 Depth=1
	movl	8(%rsp), %eax
	decl	%eax
	cltq
	incl	164(%rsp,%rax,4)
.LBB0_3:                                # %.36
                                        # =>This Inner Loop Header: Depth=1
	callq	readInteger
	movl	%eax, 8(%rsp)
	testl	%eax, %eax
	jne	.LBB0_4
# BB#5:                                 # %.60
	movl	$0, 4(%rsp)
	.align	16, 0x90
.LBB0_6:                                # %.73
                                        # =>This Inner Loop Header: Depth=1
	movslq	4(%rsp), %rax
	movl	164(%rsp,%rax,4), %edi
	callq	writeInteger
	movl	4(%rsp), %eax
	incl	%eax
	movl	%eax, 4(%rsp)
	cmpl	$9, %eax
	jne	.LBB0_6
# BB#7:                                 # %exit
	xorl	%edi, %edi
	callq	exit
	addq	$200, %rsp
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc


	.section	".note.GNU-stack","",@progbits
