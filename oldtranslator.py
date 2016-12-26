# VM to ASM translator by Joseph Ryan

# List of arithmetic operations
arithmetic = ["add", "sub", "neg", "eq", "gt", "lt", "and", "not", "or"]

# Container to hold and parse information of a single command


class Command:

    def __init__(self, rawString):
        self.commandType = ""
        self.arg1 = ""
        self.arg2 = ""
        if rawString in arithmetic:
            self.commandType = "C_ARITHMETIC"
            self.arg1 = rawString
        else:
            temp = rawString[0:rawString.find(' ')]
            if temp == "push":
                self.commandType = "C_PUSH"
                self.arg1 = rawString[rawString.find(' ') + 1:rawString.rfind(' ')]
                self.arg2 = rawString[rawString.rfind(' ') + 1:]
            if temp == "pop":
                self.commandType = "C_POP"
                self.arg1 = rawString[rawString.find(' ') + 1:rawString.rfind(' ')]
                self.arg2 = rawString[rawString.rfind(' ') + 1:]

# Class for parsing and encapsulating .vm files into distinct commands


class Parser:
    commands = []

    def __init__(self, fileName):
        f = open(fileName)
        for line in f.readlines():
            if not (line == "\n" or line[0] == '/'):
                line = line.strip()
                self.commands.append(Command(line))
        f.close()

# Class for translating VM commands into an equivilant sequence of assembly commands


class Writer:

    def __init__(self, fileName):
        self.eqlbl = 0
        self.gtlbl = 0
        self.ltlbl = 0
        self.f = open(fileName[0:fileName.find('.')] + ".asm", "w")
        self.f.write("@256" + "\n")
        self.f.write("D=A" + "\n")
        self.f.write("@SP" + "\n")
        self.f.write("M=D" + "\n")

    def __del__(self):
        self.f.write("(END)" + "\n")
        self.f.write("@END" + "\n")
        self.f.write("0;JMP" + "\n")
        if self.eqlbl > 0:
            self.eq()
        if self.ltlbl > 0:
            self.lt()
        if self.gtlbl > 0:
            self.gt()
        self.f.close()

    def eq(self):
        self.f.write("(EQ)" + "\n")
        self.f.write("@R13" + "\n")
        self.f.write("M=D" + "\n")
        self.popD()
        self.f.write("A=A-1" + "\n")
        self.f.write("D=M-D" + "\n")
        self.f.write("M=-1" + "\n")
        self.f.write("@ISEQ" + "\n")
        self.f.write("D;JEQ" + "\n")
        self.f.write("@SP" + "\n")
        self.f.write("A=M-1" + "\n")
        self.f.write("M=0" + "\n")
        self.f.write("(ISEQ)" + "\n")
        self.f.write("@R13" + "\n")
        self.f.write("A=M" + "\n")
        self.f.write("0;JMP" + "\n")

    def gt(self):
        self.f.write("(GT)" + "\n")
        self.f.write("@R13" + "\n")
        self.f.write("M=D" + "\n")
        self.popD()
        self.f.write("A=A-1" + "\n")
        self.f.write("D=M-D" + "\n")
        self.f.write("M=-1" + "\n")
        self.f.write("@ISGT" + "\n")
        self.f.write("D;JGT" + "\n")
        self.f.write("@SP" + "\n")
        self.f.write("A=M-1" + "\n")
        self.f.write("M=0" + "\n")
        self.f.write("(ISGT)" + "\n")
        self.f.write("@R13" + "\n")
        self.f.write("A=M" + "\n")
        self.f.write("0;JMP" + "\n")

    def lt(self):
        self.f.write("(LT)" + "\n")
        self.f.write("@R13" + "\n")
        self.f.write("M=D" + "\n")
        self.popD()
        self.f.write("A=A-1" + "\n")
        self.f.write("D=M-D" + "\n")
        self.f.write("M=-1" + "\n")
        self.f.write("@ISLT" + "\n")
        self.f.write("D;JLT" + "\n")
        self.f.write("@SP" + "\n")
        self.f.write("A=M-1" + "\n")
        self.f.write("M=0" + "\n")
        self.f.write("(ISLT)" + "\n")
        self.f.write("@R13" + "\n")
        self.f.write("A=M" + "\n")
        self.f.write("0;JMP" + "\n")

    def pushD(self):
        self.f.write("@SP" + "\n")
        self.f.write("M=M+1" + "\n")
        self.f.write("A=M-1" + "\n")
        self.f.write("M=D" + "\n")

    def popD(self):
        self.f.write("@SP" + "\n")
        self.f.write("AM=M-1" + "\n")
        self.f.write("D=M" + "\n")

    def writePush(self, current):
        if current.arg1 == "constant":
            self.f.write("@" + current.arg2 + "\n")
            self.f.write("D=A" + "\n")
        elif current.arg1 == "static":
            self.f.write("@" + self.staticName + current.arg2 + "\n")
            self.f.write("D=M" + "\n")
        else:
            if current.arg1 == "local":
                self.f.write("@LCL" + "\n")
            elif current.arg1 == "argument":
                self.f.write("@ARG" + "\n")
            elif current.arg1 == "this":
                self.f.write("@THIS" + "\n")
            elif current.arg1 == "that":
                self.f.write("@THAT" + "\n")
            elif current.arg1 == "temp":
                self.f.write("@5" + "\n")
            elif current.arg1 == "pointer":
                self.f.write("@3" + "\n")
            if current.arg1 != "temp" and current.arg1 != "pointer":
                self.f.write("A=M" + "\n")
            if int(current.arg2) > 0:
                self.f.write("D=A" + "\n")
                self.f.write("@" + current.arg2 + "\n")
                self.f.write("D=D+A" + "\n")
                self.f.write("A=D" + "\n")
            self.f.write("D=M" + "\n")
        self.pushD()

    def writePop(self, current):
        if current.arg1 == "local":
            self.f.write("@LCL" + "\n")
        elif current.arg1 == "argument":
            self.f.write("@ARG" + "\n")
        elif current.arg1 == "this":
            self.f.write("@THIS" + "\n")
        elif current.arg1 == "that":
            self.f.write("@THAT" + "\n")
        elif current.arg1 == "temp":
            self.f.write("@5" + "\n")
            self.f.write("D=A" + "\n")
        elif current.arg1 == "pointer":
            self.f.write("@3" + "\n")
            self.f.write("D=A" + "\n")
        elif current.arg1 == "static":
            self.f.write("@" + self.staticName + current.arg2 + "\n")
            self.f.write("D=A" + "\n")
        if current.arg1 != "temp" and current.arg1 != "pointer" and current.arg1 != "static":
            self.f.write("D=M" + "\n")
        if int(current.arg2) > 0 and current.arg1 != "static":
            self.f.write("@" + current.arg2 + "\n")
            self.f.write("D=D+A" + "\n")
        self.f.write("@R13" + "\n")
        self.f.write("M=D" + "\n")
        self.popD()
        self.f.write("@R13" + "\n")
        self.f.write("A=M" + "\n")
        self.f.write("M=D" + "\n")

    def writeArith(self, current):
        if current.arg1 == "add":
            self.popD()
            self.f.write("A=A-1" + "\n")
            self.f.write("M=D+M" + "\n")
        elif current.arg1 == "neg":
            self.f.write("@SP" + "\n")
            self.f.write("A=M-1" + "\n")
            self.f.write("M=-M" + "\n")
        elif current.arg1 == "sub":
            self.popD()
            self.f.write("A=A-1" + "\n")
            self.f.write("M=M-D" + "\n")
        elif current.arg1 == "and":
            self.popD()
            self.f.write("A=A-1" + "\n")
            self.f.write("M=D&M" + "\n")
        elif current.arg1 == "or":
            self.popD()
            self.f.write("A=A-1" + "\n")
            self.f.write("M=D|M" + "\n")
        elif current.arg1 == "not":
            self.f.write("@SP" + "\n")
            self.f.write("A=M-1" + "\n")
            self.f.write("M=!M" + "\n")
        elif current.arg1 == "eq":
            self.f.write("@LBLEQ" + str(self.eqlbl) + "\n")
            self.f.write("D=A" + "\n")
            self.f.write("@EQ" + "\n")
            self.f.write("0;JMP" + "\n")
            self.f.write("(LBLEQ" + str(self.eqlbl) + ")" + "\n")
            self.eqlbl += 1
        elif current.arg1 == "lt":
            self.f.write("@LBLLT" + str(self.ltlbl) + "\n")
            self.f.write("D=A" + "\n")
            self.f.write("@LT" + "\n")
            self.f.write("0;JMP" + "\n")
            self.f.write("(LBLLT" + str(self.ltlbl) + ")" + "\n")
            self.ltlbl += 1
        elif current.arg1 == "gt":
            self.f.write("@LBLGT" + str(self.gtlbl) + "\n")
            self.f.write("D=A" + "\n")
            self.f.write("@GT" + "\n")
            self.f.write("0;JMP" + "\n")
            self.f.write("(LBLGT" + str(self.gtlbl) + ")" + "\n")
            self.gtlbl += 1

    def writeFile(self, parse, staticFileName):
        self.staticName = staticFileName
        for line in p.commands:
            # DEBUG	print "Type:", line.commandType, "     Arg1:", line.arg1, "     Arg2:", line.arg2
            if line.commandType == "C_ARITHMETIC":
                self.writeArith(line)
            elif line.commandType == "C_PUSH":
                self.writePush(line)
            elif line.commandType == "C_POP":
                self.writePop(line)


# Open file
fileName = raw_input("Input file name ")
# fileName="StaticTest.vm"
if fileName.endswith(".vm"):
    p = Parser(fileName)
    w = Writer(fileName)
    w.writeFile(p, fileName[0:fileName.find('.')])
else:
    w = Writer(fileName + '.')
    for currentFile in os.listdir(fileName):
        if currentFile.endswith(".vm"):
            p = Parser(currentFile)
            w.writeFile(p, currentFile[0:fileName.find('.')])
