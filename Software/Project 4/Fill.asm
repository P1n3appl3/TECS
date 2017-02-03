// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

	@24576
	D=A
	@R0
	M=D
	@START
	0;JMP
(CLEAR)
	@R1
	M=0
	@START
	0;JMP
(FILL)
	@R1
	M=-1
(START)
	@SCREEN
	D=A
	@R2
	M=D
(LOOP)
	@R1
	D=M
	@R2
	A=M
	M=D
	@R2
	M=M+1
	D=M
	@R0
	D=D-M
	@CHECK
	D;JEQ
	@LOOP
	0;JMP
(CHECK)
	@KBD
	D=M
	@CLEAR
	D;JEQ
	@FILL
	0;JMP