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
        self.f.write("@HALTLOOP\n0;JMP\n")

    def writeLabel(self, lbl):
        self.f.write('(' + self.currentFunction + '$' + lbl + ')\n')

    def writeGoto(self, lbl):
        self.f.write('@' + self.currentFunction + '$' + lbl + "\n0;JMP\n")

    def writeIf(self, lbl):
        self.f.write("@SP\nAM=M-1\nD=M\n@" +
                     self.currentFunction + '$' + lbl + "\nD;JNE\n")

    def writeFunction(self, functionName, localNum):
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
        returnAddress = "ReturnAddress" + str(self.labelNum["call"])
        self.f.write("@" + functionName + "\nD=A\n@R13\nM=D\n@" + str(argNum + 5) +
                     "\nD=A\n@R14\nM=D\n@" + returnAddress + "\nD=A\n@CALLLBL\n0;JMP\n(" + returnAddress + ")\n")
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
        self.f.write("(HALTLOOP)\n@HALTLOOP\n0;JMP\n(EQLBL)\n@R13\nD=M\n@TRUELBL\nD;JEQ\n@FALSELBL\n0;JMP\n(GTLBL)\n@R13\nD=M\n@TRUELBL\nD;JGT\n@FALSELBL\n0;JMP\n(LTLBL)\n@R13\nD=M\n@TRUELBL\nD;JLT\n@FALSELBL\n0;JMP\n(TRUELBL)\n@SP\nA=M-1\nM=-1\n@14\nA=M\n0;JMP\n(FALSELBL)\n@SP\nA=M-1\nM=0\n@14\nA=M\n0;JMP\n(RETURNLBL)\n@5\nD=A\n@LCL\nA=M-D\nD=M\n@R13\nM=D\n@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\nD=A+1\n@SP\nM=D\n@LCL\nAM=M-1\nD=M\n@THAT\nM=D\n@LCL\nAM=M-1\nD=M\n@THIS\nM=D\n@LCL\nAM=M-1\nD=M\n@ARG\nM=D\n@LCL\nA=M-1\nD=M\n@LCL\nM=D\n@R13\nA=M\n0;JMP\n(CALLLBL)\n@SP\nM=M+1\nA=M-1\nM=D\n@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@ARG\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n@R14\nD=M\n@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@R13\nA=M\n0;JMP\n")
        self.f.close()
