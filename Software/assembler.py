# ASM to HACK assembler by Joseph Ryan
import sys

if len(sys.argv) > 1:
    # Opens file
    fileName = sys.argv[-1]
    if not fileName.endswith(".asm"):
        fileName += ".asm"
    f = open(fileName)

    if '-m' not in sys.argv:
        print "Input file opened\nParsing code"

    # Initializes symbol table
    symbols = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4, "SCREEN": 16384, "KBD": 24576, "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15}

    # Reads file into list
    program = []
    for line in f.readlines():
        if not (line == "\n" or line[0] == '/'):
            if line.find('/') > -1:
                line = line[0:line.find('/')]
            line = line.strip()
            program.append(line)
    f.close()

    if '-m' not in sys.argv:
        print "Reading symbols"

    # Adds jump symbols to table
    i = 0
    j = 16
    for command in program:
        if command.startswith('('):
            symbols[command[1:-1]] = i
            i -= 1
        i += 1

    # Adds A instruction symbols to table, and replaces symbols with numeric equivilants
    for command in program:
        if command.startswith('@'):
            if not command[1:].isdigit():
                if symbols.has_key(command[1:]):
                    command = '@' + str(symbols.get(command[1:]))
                else:
                    symbols[command[1:]] = j
                    j += 1

    if '-m' not in sys.argv:
        print "Assembling code"

    # Translates instructions into hack op codes
    hack = []
    for command in program:
        # A instructions
        if command.startswith('@'):
            load = command.split('@')[1]
            if not load.isdigit():
                load = str(symbols[load])
            hack.append(bin(int(load))[2:])
            hack[len(hack) - 1] = hack[len(hack) - 1].zfill(16)
    # C instructions
        elif not command.startswith('('):
            hack.append("111")
            if command.find('=') > -1:
                comp = command.split('=')[1]
            else:
                comp = command
            if command.find(';') > -1:
                comp = comp.split(';')[0]
    # Computation
            hack[len(hack) - 1] += str(int(comp.find('M') > -1))
            if comp == '0':
                hack[len(hack) - 1] += "101010"
            if comp == '1':
                hack[len(hack) - 1] += "111111"
            if comp == "-1":
                hack[len(hack) - 1] += "111010"
            if comp == 'D':
                hack[len(hack) - 1] += "001100"
            if comp == 'A' or comp == 'M':
                hack[len(hack) - 1] += "110000"
            if comp == "!D":
                hack[len(hack) - 1] += "001101"
            if comp == "!A" or comp == "!M":
                hack[len(hack) - 1] += "110001"
            if comp == "-D":
                hack[len(hack) - 1] += "001101"
            if comp == "-A" or comp == "-M":
                hack[len(hack) - 1] += "110001"
            if comp == "D+1":
                hack[len(hack) - 1] += "011111"
            if comp == "A+1" or comp == "M+1":
                hack[len(hack) - 1] += "110111"
            if comp == "D-1":
                hack[len(hack) - 1] += "001110"
            if comp == "A-1" or comp == "M-1":
                hack[len(hack) - 1] += "110010"
            if comp == "D+A" or comp == "D+M":
                hack[len(hack) - 1] += "000010"
            if comp == "D-A" or comp == "D-M":
                hack[len(hack) - 1] += "010011"
            if comp == "A-D" or comp == "M-D":
                hack[len(hack) - 1] += "000111"
            if comp == "D&A" or comp == "D&M":
                hack[len(hack) - 1] += "000000"
            if comp == "D|A" or comp == "D|M":
                hack[len(hack) - 1] += "010101"
    # Destination
            if command.find('=') > -1:
                dest = command.split('=')[0]
                hack[len(hack) - 1] += str(int(dest.find('A') > -1))
                hack[len(hack) - 1] += str(int(dest.find('D') > -1))
                hack[len(hack) - 1] += str(int(dest.find('M') > -1))
            else:
                hack[len(hack) - 1] += "000"
    # Jump
            if command.find(';') > -1:
                jmp = command.split(';')[1][1:3]
                if jmp == "GT":
                    hack[len(hack) - 1] += "001"
                if jmp == "EQ":
                    hack[len(hack) - 1] += "010"
                if jmp == "GE":
                    hack[len(hack) - 1] += "011"
                if jmp == "LT":
                    hack[len(hack) - 1] += "100"
                if jmp == "NE":
                    hack[len(hack) - 1] += "101"
                if jmp == "LE":
                    hack[len(hack) - 1] += "110"
                if jmp == "MP":
                    hack[len(hack) - 1] += "111"
            else:
                hack[len(hack) - 1] += "000"

    if '-m' not in sys.argv:
        print "Writing output to file"

    # Write resulting binary
    f = open(fileName[:-3] + "hack", "w")
    for line in hack:
        if '-p' in sys.argv:
            print line
        f.write(line + "\n")
    if '-m' not in sys.argv:
        print "Assembly Complete"

else:
    print "usage: assembler.py sourceFile[.asm]\noptions:\n\t-m mutes status messages\n\t-p prints output to stdout"
