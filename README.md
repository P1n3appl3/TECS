# The Elements of Computing Systems
nand2tetris course work

# Software
## Compiler (.jack -> .vm)
```
usage: python Software/Compiler/main.py [options] source[.jack]
        sourceFile(s) may be file or directory.
options:
        -m mutes status messages
        -x creates syntax analysis xml file
```
## VM Translator (.vm -> .asm)
```
usage: python Software/VMTranslator/main.py [options] source[.vm]
        sourceFile(s) may be file or directory.
options:
        -m mutes status messages
        -c writes vm commands as comments in .asm file
        -b doesn't generate bootstrap code
        -l creates source.debug with adjusted line numbers
```
## Assembler (.asm -> .hack)
```
usage: python Software/assembler.py sourceFile[.asm]
options:
        -m mutes status messages
        -p prints output to stdout
```

# Hardware
- Add16(a= ,b= ,out= );
- ALU(x= ,y= ,zx= ,nx= ,zy= ,ny= ,f= ,no= ,out= ,zr= ,ng= );
- And16(a= ,b= ,out= );
- And(a= ,b= ,out= );
- ARegister(in= ,load= ,out= );
- Bit(in= ,load= ,out= );
- CPU(inM= ,instruction= ,reset= ,outM= ,writeM= ,addressM= ,pc= );
- DFF(in= ,out= );
- DMux4Way(in= ,sel= ,a= ,b= ,c= ,d= );
- DMux8Way(in= ,sel= ,a= ,b= ,c= ,d= ,e= ,f= ,g= ,h= );
- DMux(in= ,sel= ,a= ,b= );
- DRegister(in= ,load= ,out= );
- FullAdder(a= ,b= ,c= ,sum= ,carry= );
- HalfAdder(a= ,b= ,sum= , carry= );
- Inc16(in= ,out= );
- Keyboard(out= );
- Memory(in= ,load= ,address= ,out= );
- Mux16(a= ,b= ,sel= ,out= );
- Mux4Way16(a= ,b= ,c= ,d= ,sel= ,out= );
- Mux8Way16(a= ,b= ,c= ,d= ,e= ,f= ,g= ,h= ,sel= ,out= );
- Mux(a= ,b= ,sel= ,out= );
- Nand(a= ,b= ,out= );
- Not16(in= ,out= );
- Not(in= ,out= );
- Or16(a= ,b= ,out= );
- Or(a= ,b= ,out= );
- Or8Way(in= ,out= );
- PC(in= ,load= ,inc= ,reset= ,out= );
- RAM16K(in= ,load= ,address= ,out= );
- RAM512(in= ,load= ,address= ,out= );
- RAM4K(in= ,load= ,address= ,out= );
- RAM64(in= ,load= ,address= ,out= );
- RAM8(in= ,load= ,address= ,out= );
- Register(in= ,load= ,out= );
- ROM32K(address= ,out= );
- Screen(in= ,load= ,address= ,out= );
- Xor(a= ,b= ,out= );

# Project 13
A list of all additions and modifications made outside the domain of the course.
- Add modulus functionality to jack with Math.mod() and make the compiler properly interpret the % symbol
- Add pseudo-random number generation to jack (via a linear congruential generator) with Math.seedRandom(), Math.rand(), and Math.randRange()
