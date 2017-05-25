# JACK to VM compiler by Joseph Ryan
import sys
import os


class Tokenizer:
    symbols = "{}()[].,;+-*/&|~<>="
    keywords = ["do", "if", "var", "int", "let", "null", "this", "else", "char", "true", "void", "class", "field", "false", "while", "static", "return", "method", "boolean", "function", "constructor"]

    def __init__(self, fileName):
        self.reader = open(fileName)
        self.token = ""
        self.tokenType = ""
        self.line = self.reader.readline().lstrip(' \t')

    def parseInt(self):
        i = 1
        while self.line[i].isdigit():
            i += 1
        self.tokenType = "integerConstant"
        self.token = self.line[:i]
        self.line = self.line[i:]

    def parseString(self):
        self.tokenType = "stringConstant"
        self.token = self.line.split('"')[1]
        self.line = '"'.join(self.line.split('"')[2:])

    def parseSymbol(self):
        self.tokenType = "symbol"
        self.token = self.line[0]
        self.line = self.line[1:]

    def parseKeyword(self):
        for i in range(2, max(len(self.line), 11)):
            if self.line[:i] in self.keywords:
                self.tokenType = "keyword"
                self.token = self.line[:i]
                self.line = self.line[i:]
                return True
        return False

    def parseIdentifier(self):
        i = 1
        while self.line[i].isalnum() or self.line[i] == '_':
            i += 1
        self.tokenType = "identifier"
        self.token = self.line[:i]
        self.line = self.line[i:]

    def skip(self):
        while True:
            if self.line == "\n" or self.line[:2] == "//":  # skip single line comments and empty lines
                self.line = self.reader.readline().lstrip(' \t')
            elif self.line[:2] == "/*":  # skip everything until end of block/api comment is found
                while "*/" not in self.line:
                    self.line = self.reader.readline().lstrip(' \t')
                    if self.line == "":
                        return False
                self.line = self.line[self.line.find("*/") + 2:]
            elif self.line == "":  # readline() only reads empty string at EOF
                return False
            else:
                return True

    def advance(self):
        self.line = self.line.lstrip(' \t')
        if not self.skip():
            return False
        if self.line[0].isdigit():
            self.parseInt()
        elif self.line[0] in self.symbols:
            self.parseSymbol()
        elif self.line[0] == '"':
            self.parseString()
        else:
            if not self.parseKeyword():
                self.parseIdentifier()
        return True


class CompilationEngine:

    def __init__(self, fileName):
        if '-x' in sys.argv:
            self.writer = open(fileName.split('.')[0] + ".xml", 'w')
        self.t = Tokenizer(fileName)
        self.t.advance()
        self.vm = VMWriter(fileName)
        self.table = None
        self.classTable = SymbolTable()

    def writeXML(self, s):
        if '-x' in sys.argv:
            self.writer.write(s + '\n')

    def writeToken(self, n=1):
        for i in range(n):
            tempType = '<' + self.t.tokenType + '>'
            tempToken = self.t.token.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            self.writeXML('<' + self.t.tokenType + '> ' + tempToken + ' </' + self.t.tokenType + '>')
            self.t.advance()

    def compileClass(self):
        self.writeXML("<class>")
        self.writeToken()
        self.className = self.t.token
        self.writeToken(2)
        while self.t.token in ("static", "field"):
            self.compileClassVarDec()
        while self.t.token != '}':
            self.compileSubroutine()
        self.writeToken()
        self.writeXML("</class>")

    def compileClassVarDec(self):
        self.writeXML("<classVarDec>")
        while self.t.token != ';':
            self.writeToken()
        self.writeToken()
        self.writeXML("</classVarDec>")

    def compileSubroutine(self):
        self.whileCount = 0
        self.ifCount = 0
        self.writeXML("<subroutineDec>")
        self.table = SymbolTable()
        self.writeToken()
        self.functionType = self.t.token
        self.writeToken()
        functionName = self.t.token
        self.writeToken(2)
        self.compileParameterList()
        self.writeToken()
        self.writeXML("<subroutineBody>")
        self.writeToken()
        while self.t.token == "var":
            self.compileVarDec()
        varNum = len([i for i in self.table.table if self.table.getKind(i) == "local"])
        self.vm.writeFunction(self.className + '.' + functionName, varNum)
        self.compileStatements()
        self.writeToken()
        self.writeXML("</subroutineBody>")
        self.writeXML("</subroutineDec>")

    def compileParameterList(self):
        self.writeXML("<parameterList>")
        while self.t.token != ')':
            type = self.t.token
            self.writeToken()
            self.table.add(self.t.token, type, "argument")
            self.writeToken()
            if self.t.token == ',':
                self.writeToken()
        self.writeXML("</parameterList>")

    def compileVarDec(self):
        self.writeXML("<varDec>")
        self.writeToken()
        type = self.t.token
        self.writeToken()
        while self.t.token != ';':
            if self.t.token != ',':
                self.table.add(self.t.token, type, "local")
            self.writeToken()
        self.writeToken()
        self.writeXML("</varDec>")

    def compileStatements(self):
        self.writeXML("<statements>")
        while self.t.token != '}':
            if self.t.token == 'let':
                self.compileLet()
            elif self.t.token == 'do':
                self.compileDo()
            elif self.t.token == 'if':
                self.compileIf()
            elif self.t.token == 'while':
                self.compileWhile()
            elif self.t.token == 'return':
                self.compileReturn()
        self.writeXML("</statements>")

    def compileDo(self):
        self.writeXML("<doStatement>")
        self.writeToken()
        name = self.t.token
        self.writeToken()
        if self.t.token == '.':
            self.writeToken()
            name += '.' + self.t.token
            self.writeToken()
        self.writeToken()
        argNum = self.compileExpressionList()
        self.writeToken(2)
        self.vm.writeCall(name, argNum)
        self.vm.writePop("temp", 0)
        self.writeXML("</doStatement>")

    def compileLet(self):
        self.writeXML("<letStatement>")
        self.writeToken()
        name = self.t.token
        self.writeToken()
        if self.t.token == '[':
            self.writeToken()
            self.compileExpression()
            self.writeToken()
        self.writeToken()
        self.compileExpression()
        self.writeToken()
        t = self.table
        if not t.has(name):
            t = self.classTable
        if t.getKind(name) != "field":
            self.vm.writePop(t.getKind(name), t.getCount(name))
        else:
            pass
            # object handling
        self.writeXML("</letStatement>")

    def compileWhile(self):
        currentCount = self.whileCount
        self.whileCount += 1
        self.writeXML("<whileStatement>")
        self.writeToken(2)
        self.vm.writeLabel("WHILE_EXP" + str(currentCount))
        self.compileExpression()
        self.vm.writeUnary('~')
        self.vm.writeIf("WHILE_END" + str(currentCount))
        self.writeToken(2)
        self.compileStatements()
        self.vm.writeGoto("WHILE_EXP" + str(currentCount))
        self.writeToken()
        self.vm.writeLabel("WHILE_END" + str(currentCount))
        self.writeXML("</whileStatement>")

    def compileIf(self):
        currentCount = self.ifCount
        self.ifCount += 1
        self.writeXML("<ifStatement>")
        self.writeToken(2)
        self.compileExpression()
        self.vm.writeIf("IF_TRUE" + str(currentCount))
        self.vm.writeGoto("IF_FALSE" + str(currentCount))
        self.vm.writeLabel("IF_TRUE" + str(currentCount))
        self.writeToken(2)
        self.compileStatements()
        self.writeToken()
        self.vm.writeGoto("IF_END" + str(currentCount))
        self.vm.writeLabel("IF_FALSE" + str(currentCount))
        if self.t.token == "else":
            self.writeToken(2)
            self.compileStatements()
            self.writeToken()
        self.vm.writeLabel("IF_END" + str(currentCount))
        self.writeXML("</ifStatement>")

    def compileReturn(self):
        self.writeXML("<returnStatement>")
        self.writeToken()
        if self.t.token != ';':
            self.compileExpression()
        self.writeToken()
        if self.functionType == "void":
            self.vm.writePush("constant", 0)
        self.vm.writeReturn()
        self.writeXML("</returnStatement>")

    def compileExpressionList(self):
        self.writeXML("<expressionList>")
        n = 0
        if self.t.token != ')':
            self.compileExpression()
            n = 1
        while self.t.token == ',':
            n += 1
            self.writeToken()
            self.compileExpression()
        self.writeXML("</expressionList>")
        return n

    def compileExpression(self):
        self.writeXML("<expression>")
        self.compileTerm()
        while self.t.token in "+-*/&|~<>=":
            op = self.t.token
            self.writeToken()
            self.compileTerm()
            self.vm.writeArithmetic(op)
        self.writeXML("</expression>")

    def compileTerm(self):
        self.writeXML("<term>")
        if self.t.token in "~-":
            op = self.t.token
            self.writeToken()
            self.compileTerm()
            self.vm.writeUnary(op)
        elif self.t.token == '(':
            self.writeToken()
            self.compileExpression()
            self.writeToken()
        elif self.t.tokenType != "identifier":
            if self.t.tokenType == "integerConstant":
                self.vm.writePush("constant", self.t.token)
            elif self.t.token in ("true", "false"):
                self.vm.writePush("constant", 0)
                if self.t.token == "true":
                    self.vm.writeUnary('~')
            else:
                # string code
                pass
            self.writeToken()
        else:
            name = self.t.token
            self.writeToken()
            if self.t.token == '[':
                self.writeToken()
                self.compileExpression()
                self.writeToken()
            elif self.t.token in "(.":
                if self.t.token == '.':
                    self.writeToken()
                    name += '.' + self.t.token
                    self.writeToken()
                self.writeToken()
                argNum = self.compileExpressionList()
                self.writeToken()
                self.vm.writeCall(name, argNum)
            else:
                t = self.table
                if not t.has(name):
                    t = self.classTable
                if t.getKind(name) != "field":
                    self.vm.writePush(t.getKind(name), t.getCount(name))
                else:
                    pass
                    # object handling
        self.writeXML("</term>")


class SymbolTable:

    def __init__(self):
        self.count = {"static": 0, "field": 0, "argument": 0, "local": 0}
        self.table = {}

    def __str__(self):
        n = ""
        for i in self.table:
            n += i + ' ' + str(self.table[i]) + '\n'
        return n

    def has(self, n):
        return n in self.table

    def add(self, n, type, kind):
        self.table[n] = (type, kind, self.count[kind])
        self.count[kind] += 1

    def getType(self, n):
        return self.table[n][0]

    def getKind(self, n):
        return self.table[n][1]

    def getCount(self, n):
        return self.table[n][2]


class VMWriter:

    def __init__(self, fileName):
        self.writer = open(fileName.split('.')[0] + ".vm", 'w')

    def writeArithmetic(self, op):
        self.writer.write({'+': "add", '-': "sub", '>': "gt", '<': "lt", '&': "and", '|': "or", '=': "eq", '*': "call Math.multiply 2", '/': "call Math.divide 2"}[op] + '\n')

    def writeUnary(self, op):
        self.writer.write({'-': "neg", '~': "not"}[op] + '\n')

    def writeFunction(self, name, args):
        self.writer.write("function " + name + ' ' + str(args) + '\n')

    def writePush(self, type, n):
        self.writer.write("push " + type + ' ' + str(n) + '\n')

    def writePop(self, type, n):
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


if len(sys.argv) > 1:
    files = []
    fName = sys.argv[-1].replace('\\', '/')
    if fName.endswith(".jack"):
        files.append(fName)
    else:
        for i in os.listdir(fName):
            if i.endswith(".jack"):
                files.append(fName + '/' + i)
    for f in files:
        c = CompilationEngine(f)
        c.compileClass()
else:
    print "usage: compiler.py [options] source[.jack]\n\tsourceFile(s) may be file or directory.\noptions:\n\t-x write syntax analysis xml file"
