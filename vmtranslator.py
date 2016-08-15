#VM to ASM translator by Joseph Ryan
import sys
import os

#Handles input parsing and sanatization
class Parser:
	currentLine = 0
	def __init__(self, fileName):
		reader = open(fileName)
		self.lines = filter(None, [i.split('/',1)[0].strip() for i in reader])
		reader.close()

	def hasMoreCommands(self):
		return self.currentLine<len(self.lines)

	def advance(self):
		self.currentLine+=1

	def commandType(self):
		temp = self.lines[self.currentLine].split(' ')[0]
		if temp in ["add","sub","neg","eq","gt","lt","and","not","or"]:
			return "C_ARITHMETIC"
		elif temp == "push":
			return "C_PUSH"
		elif temp == "pop":
			return "C_POP"

	def arg1(self):
		temp = self.lines[self.currentLine].split(' ')
		return temp[0 if self.commandType() == "C_ARITHMETIC" else 1]

	def arg2(self):
		return int(self.lines[self.currentLine].split(' ')[2])

#Translates vm code and writes assembly to output file
class CodeWriter:
	def __init__(self, fileName):
		self.f = open(fileName + ".asm", 'w')
		self.labelNum = 0

	def setFile(self, fileName):
		self.currentFile = fileName.split('/')[-1].split('.')[0]

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
				self.f.write("D=M-D\n@R13\nM=D\n@"+command.upper()+str(self.labelNum)+"\nD=A\n@R14\nM=D\n@"+command.upper()+"LBL\n0;JMP\n("+command.upper()+str(self.labelNum)+")\n")
				self.labelNum+=1

	def writePushPop(self, command, segment, index):
		segmentNames = {"local":"LCL", "argument":"ARG","this":"THIS","that":"THAT","temp":"R5","pointer":"R3"}
		if command == "C_PUSH":
			if segment == "constant":
				self.f.write("@"+str(index)+"\nD=A\n")
			elif segment == "static":
				self.f.write("@"+self.currentFile+str(index)+"\nD=M\n")
			else:
				self.f.write("@"+str(segmentNames[segment])+"\n")
				if segment not in {"pointer", "temp"}:
					self.f.write("A=M\n")
				if index > 0:
					self.f.write("D=A\n@"+str(index)+"\nD=D+A\nA=D\n")
				self.f.write("D=M\n")
			self.f.write("@SP\nM=M+1\nA=M-1\nM=D\n")
		else:
			if segment == "static":
				self.f.write("@SP\nAM=M-1\nD=M\n@"+self.currentFile+str(index)+"\nM=D\n")
			elif index < 6:
				self.f.write("@SP\nAM=M-1\nD=M\n@"+str(segmentNames[segment])+"\n")
				if segment not in {"pointer", "temp"}:
					self.f.write("A=M\n")
				for i in range(index):
					self.f.write("A=A+1\n")
				self.f.write("M=D\n")
			else:
				self.f.write("@"+str(index)+"\nD=A\n@"+str(segmentNames[segment])+"\nD=D+")
				self.f.write("M" if segment not in {"pointer", "temp"} else "A")
				self.f.write("\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")

	def close(self):
		self.f.write("(END)\n@END\n0;JMP\n")
		self.f.write("(EQLBL)\n@R13\nD=M\n@TRUELBL\nD;JEQ\n@FALSELBL\n0;JMP\n")
		self.f.write("(GTLBL)\n@R13\nD=M\n@TRUELBL\nD;JGT\n@FALSELBL\n0;JMP\n")
		self.f.write("(LTLBL)\n@R13\nD=M\n@TRUELBL\nD;JLT\n@FALSELBL\n0;JMP\n")
		self.f.write("(TRUELBL)\n@SP\nA=M-1\nM=-1\n@14\nA=M\n0;JMP\n")
		self.f.write("(FALSELBL)\n@SP\nA=M-1\nM=0\n@14\nA=M\n0;JMP\n")
		self.f.close()


files = []
fName = sys.argv[1]
if fName.endswith(".vm"):
	files.append(fName)
else:
	for i in os.listdir(fName):
	    if i.endswith(".vm"):
	    	files.append(fName +'/'+ i)

cw = CodeWriter(fName.split('.')[0])
for f in files:
	p = Parser(f)
	cw.setFile(f)
	while p.hasMoreCommands():
		c = p.commandType()
		cw.f.write("//"+p.lines[p.currentLine]+'\n')
		if c == "C_ARITHMETIC":
			cw.writeArithmetic(p.arg1())
		elif c in {"C_PUSH", "C_POP"}:
			cw.writePushPop(c, p.arg1(), p.arg2())
		p.advance()
cw.close()