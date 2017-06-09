class VMWriter:

    def __init__(self, fileName):
        self.writer = open(fileName.split('.')[0] + ".vm", 'w')

    def writeArithmetic(self, op):
        self.writer.write({'+': "add", '-': "sub", '>': "gt", '<': "lt", '>=': "lt\nnot", '<=': "gt\nnot", '~=': "eq\nnot", '&': "and", '|': "or", '=': "eq", '==': "eq", '*': "call Math.multiply 2", '/': "call Math.divide 2", '%': "call Math.mod 2"}[op] + '\n')

    def writeUnary(self, op):
        self.writer.write({'-': "neg", '~': "not"}[op] + '\n')

    def writeFunction(self, name, args):
        self.writer.write("function " + name + ' ' + str(args) + '\n')

    def writePush(self, type, n):
        if type == "field":
            type = "this"
        self.writer.write("push " + type + ' ' + str(n) + '\n')

    def writePop(self, type, n):
        if type == "field":
            type = "this"
        self.writer.write("pop " + type + ' ' + str(n) + '\n')

    def writeReturn(self):
        self.writer.write("return\n")

    def writeCall(self, name, args):
        self.writer.write("call " + name + ' ' + str(args) + '\n')

    def writeLabel(self, name):
        self.writer.write("label " + name + '\n')

    def writeIf(self, name):
        self.writer.write("if-goto " + name + '\n')

    def writeGoto(self, name):
        self.writer.write("goto " + name + '\n')

    def __del__(self):
        self.writer.close()
