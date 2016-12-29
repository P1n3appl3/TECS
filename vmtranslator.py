# VM to ASM translator by Joseph Ryan
import sys
import os

# Handles input parsing and sanatization


class Parser:
    currentLine = 0

    def __init__(self, fileName):
        reader = open(fileName)
        self.lines = filter(None, [i.split('/', 1)[0].strip() for i in reader])
        reader.close()

    def hasMoreCommands(self):
        return self.currentLine < len(self.lines)

    def advance(self):
        self.currentLine += 1

    def commandType(self):
        types = {"push": "C_PUSH", "pop": "C_POP", "label": "C_LABEL", "goto": "C_GOTO",
                         "if-goto": "C_IF", "function": "C_FUNCTION", "call": "C_CALL", "return": "C_RETURN"}
        temp = self.lines[self.currentLine].split(' ')[0]
        if temp in {"add", "sub", "neg", "eq", "gt", "lt", "and", "not", "or"}:
            return "C_ARITHMETIC"
        return types[temp]

    def arg1(self):
        return self.lines[self.currentLine].split(' ')[0 if self.commandType() == "C_ARITHMETIC" else 1]

    def arg2(self):
        return int(self.lines[self.currentLine].split(' ')[2])


# Translates vm code and writes assembly to output file
class CodeWriter:

    def __init__(self, fileName):
        self.f = open(fileName + ".asm", 'w')
        self.labelNum = {"eq": 0, "lt": 0, "gt": 0, "call": 0}
        self.currentFunction = ""

    def setFile(self, fileName):
        self.currentFile = fileName.split('/')[-1].split('.')[0]

    def writeInit(self):
        self.f.write("@256\nD=A\n@SP\nM=D\n")
        self.writeCall("Sys.init", 0)
        self.f.write("(END)\n@END\n0;JMP\n")

    def writeLabel(self, lbl):
        self.f.write('(' + self.currentFunction + '$' + lbl + ')\n')

    def writeGoto(self, lbl):
        self.f.write('@' + self.currentFunction + '$' + lbl + "\n0;JMP\n")

    def writeIf(self, lbl):
        self.f.write("@SP\nAM=M-1\nD=M\n@" +
                     self.currentFunction + '$' + lbl + "\nD;JNE\n")

    def writeFunction(self, functionName, localNum):
        #self.currentFunction = self.currentFile + '.' + functionName
        self.currentFunction = functionName
        self.f.write("(" + self.currentFunction + ")\n")
        if localNum == 1:
            self.f.write("@0\nD=A\nM=M+1\nA=M-1\nM=D\n")
        elif localNum > 1:
            self.f.write("@" + str(localNum) + "\nD=A\n@SP\nM=D+M\nD=A\nA=M-1\nM=D\n" +
                         "A=A-1\nM=D\n" * (localNum - 1))

    def writeReturn(self):
        self.f.write("@RETURNLBL\n0;JMP\n")

    def writeCall(self, functionName, argNum):
        returnAddress = "ret" + str(self.labelNum["call"])
        self.f.write("@" + functionName + "\nD=A\n@R13\nM=D\n@" + str(argNum + 5) + "\nD=A\n@R14\nM=D\n@" + returnAddress + "\nD=A\n@CALLLBL\n0;JMP\n(" + returnAddress + ")\n")
        self.labelNum["call"] += 1

    def writeArithmetic(self, command):
        if command in {"neg", "not"}:
            self.f.write("@SP\nA=M-1\nM=")
            if command == "neg":
                self.f.write("-M\n")
            else:
                self.f.write("!M\n")
        else:
            self.f.write("@SP\nAM=M-1\nD=M\nA=A-1\n")
            if command == "or":
                self.f.write("M=D|M\n")
            elif command == "and":
                self.f.write("M=D&M\n")
            elif command == "add":
                self.f.write("M=D+M\n")
            elif command == "sub":
                self.f.write("M=M-D\n")
            elif command in {"gt", "lt", "eq"}:
                self.f.write("D=M-D\n@R13\nM=D\n@" + command.upper() + str(self.labelNum[command]) + "\nD=A\n@R14\nM=D\n@" + command.upper(
                ) + "LBL\n0;JMP\n(" + command.upper() + str(self.labelNum[command]) + ")\n")
                self.labelNum[command] += 1

    def writePushPop(self, command, segment, index):
        segmentNames = {"local": "LCL", "argument": "ARG",
                                        "this": "THIS", "that": "THAT", "temp": "R5", "pointer": "R3"}
        if command == "C_PUSH":
            if segment == "constant":
                self.f.write("@" + str(index) + "\nD=A\n")
            elif segment == "static":
                self.f.write("@" + self.currentFile + str(index) + "\nD=M\n")
            else:
                self.f.write("@" + str(segmentNames[segment]) + "\n")
                if segment not in {"pointer", "temp"}:
                    self.f.write("A=M\n")
                if index > 0:
                    self.f.write("D=A\n@" + str(index) + "\nD=D+A\nA=D\n")
                self.f.write("D=M\n")
            self.f.write("@SP\nM=M+1\nA=M-1\nM=D\n")
        else:
            if segment == "static":
                self.f.write("@SP\nAM=M-1\nD=M\n@" +
                             self.currentFile + str(index) + "\nM=D\n")
            elif index < 6:
                self.f.write("@SP\nAM=M-1\nD=M\n@" +
                             str(segmentNames[segment]) + "\n")
                if segment not in {"pointer", "temp"}:
                    self.f.write("A=M\n")
                for i in range(index):
                    self.f.write("A=A+1\n")
                self.f.write("M=D\n")
            else:
                self.f.write("@" + str(index) + "\nD=A\n@" +
                             str(segmentNames[segment]) + "\nD=D+")
                self.f.write("M" if segment not in {
                    "pointer", "temp"} else "A")
                self.f.write("\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")

    def close(self):
        #self.f.write("(END)\n@END\n0;JMP\n")
        self.f.write("(EQLBL)\n@R13\nD=M\n@TRUELBL\nD;JEQ\n@FALSELBL\n0;JMP\n")
        self.f.write("(GTLBL)\n@R13\nD=M\n@TRUELBL\nD;JGT\n@FALSELBL\n0;JMP\n")
        self.f.write("(LTLBL)\n@R13\nD=M\n@TRUELBL\nD;JLT\n@FALSELBL\n0;JMP\n")
        self.f.write("(TRUELBL)\n@SP\nA=M-1\nM=-1\n@14\nA=M\n0;JMP\n")
        self.f.write("(FALSELBL)\n@SP\nA=M-1\nM=0\n@14\nA=M\n0;JMP\n")
        self.f.write("(RETURNLBL)\n")
        #*ARG=*SP-1
        self.f.write("@SP\n")
        self.f.write("A=M-1\n")
        self.f.write("D=M\n")
        self.f.write("@ARG\n")
        self.f.write("A=M\n")
        self.f.write("M=D\n")
        # SP=*ARG+1
        self.f.write("D=A+1\n")
        self.f.write("@SP\n")
        self.f.write("M=D\n")
        # THAT=*LCL-1
        self.f.write("@LCL\n")
        self.f.write("AM=M-1\n")
        self.f.write("D=M\n")
        self.f.write("@THAT\n")
        self.f.write("M=D\n")
        # THIS=*LCL-2
        self.f.write("@LCL\n")
        self.f.write("AM=M-1\n")
        self.f.write("D=M\n")
        self.f.write("@THIS\n")
        self.f.write("M=D\n")
        # ARG=*LCL-3
        self.f.write("@LCL\n")
        self.f.write("AM=M-1\n")
        self.f.write("D=M\n")
        self.f.write("@ARG\n")
        self.f.write("M=D\n")
        # RET=*LCL-5
        self.f.write("@LCL\n")
        self.f.write("M=M-1\n")
        self.f.write("AM=M-1\n")
        self.f.write("D=M\n")
        self.f.write("@R13\n")
        self.f.write("M=D\n")
        # LCL=*LCL-4
        self.f.write("@LCL\n")
        self.f.write("A=M+1\n")
        self.f.write("D=M\n")
        self.f.write("@LCL\n")
        self.f.write("M=D\n")
        # GOTO RET
        self.f.write("@R13\n")
        self.f.write("A=M\n")
        self.f.write("0;JMP\n")

        # push return address
        # push LCL
        # push ARG
        # push THIS
        # push THAT
        # ARG = SP-n-5 where n=number of args
        #LCL = SP
        # goto f
        #(return addr)
        # self.f.write("\n")

        self.f.write("(CALLLBL)\n@SP\nM=M+1\nA=M-1\nM=D\n@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@ARG\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@R14\nD=M\n@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@R13\nA=M\n0;JMP\n")
        self.f.close()


if len(sys.argv) > 1:
    files = []
    fName = sys.argv[-1].replace('\\', '/')
    if fName.endswith(".vm"):
        files.append(fName)
    else:
        for i in os.listdir(fName):
            if i.endswith(".vm"):
                files.append(fName + '/' + i)
    if "-m" not in sys.argv:
        print "Parsing " + str(len(files)) + " file(s)"
    cw = CodeWriter(fName.split('.')[0])
    if "-b" not in sys.argv:
        cw.writeInit()
    for f in files:
        p = Parser(f)
        cw.setFile(f)
        if "-m" not in sys.argv:
            print "Translating " + f.split('/')[-1]
        while p.hasMoreCommands():
            c = p.commandType()
            if "-c" in sys.argv:
                cw.f.write("//\t\t\t\t" + p.lines[p.currentLine] + '\n')
            if c == "C_ARITHMETIC":
                cw.writeArithmetic(p.arg1())
            elif c in {"C_PUSH", "C_POP"}:
                cw.writePushPop(c, p.arg1(), p.arg2())
            elif c == "C_LABEL":
                cw.writeLabel(p.arg1())
            elif c == "C_GOTO":
                cw.writeGoto(p.arg1())
            elif c == "C_IF":
                cw.writeIf(p.arg1())
            elif c == "C_FUNCTION":
                cw.writeFunction(p.arg1(), p.arg2())
            elif c == "C_CALL":
                cw.writeCall(p.arg1(), p.arg2())
            elif c == "C_RETURN":
                cw.writeReturn()
            p.advance()
    cw.close()
    if "-l" in sys.argv:
        lineNum = 0
        with open(fName.split('.')[0]+".asm", 'r') as src:
            with open(fName.split('.')[0]+".debug", 'w') as dest:
                for line in src:
                    if not line.startswith('(') and not line.startswith('//'):
                        dest.write(str(lineNum)+'\t\t')
                        lineNum+=1
                    dest.write(line)
    if "-m" not in sys.argv:
        print "Translation Complete"
else:
    print "usage: vmtranslator.py [options] source[.vm]\n\tsourceFile(s) may be file or directory.\noptions:\n\t-m mutes progress messages\n\t-c writes vm commands as comments in .asm file\n\t-b doesn't generate bootstrap code\n\t-l creates source.debug with adjusted line numbers"
