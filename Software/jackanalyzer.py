# JACK syntax analyzer by Joseph Ryan
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

    def getToken(self):
        return self.tokenType, self.token

    def parseInt(self):
        i=1
        while self.line[i].isdigit():
            i+=1
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
        for i in range(2,max(len(self.line), 11)):
            if self.line[:i] in self.keywords:
                self.tokenType = "keyword"
                self.token = self.line[:i]
                self.line = self.line[i:]
                return True
        return False

    def parseIdentifier(self):
        i=1
        while self.line[i].isalnum() or self.line[i]=='_':
            i+=1
        self.tokenType = "identifier"
        self.token = self.line[:i]
        self.line = self.line[i:]

    def skip(self):
        while True:
            if self.line == "\n" or self.line[:2] == "//":      #skip single line comments and empty lines
                self.line = self.reader.readline().lstrip(' \t')
            elif self.line[:2] == "/*":     #skip everything until end of block/api comment is found
                while "*/" not in self.line:
                    self.line = self.reader.readline().lstrip(' \t')
                    if self.line == "":
                        return False
                self.line = self.line[self.line.find("*/")+2:]
            elif self.line == "":       #readline() only reads empty string at EOF
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

    def __del__(self):
        self.reader.close()

class CompilationEngine:
    def __init__(self, fileName):
        self.writer = open(fileName.split('.')[0]+".xml", 'w')
        self.t = Tokenizer(fileName)
        self.t.advance()

    def writeToken(self, n=1):
        for i in range(n):
            tempType = '<' + self.t.tokenType + '>'
            tempToken = self.t.token.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
            self.writer.write('<' + self.t.tokenType + '> '+ tempToken + ' </' + self.t.tokenType + '>\n')
            self.t.advance()

    def compileClass(self):
        self.writer.write("<class>\n")
        self.writeToken(3)
        while self.t.token in ("static", "field"):
            self.compileClassVarDec()
        while self.t.token != '}':
            self.compileSubroutine()
        self.writeToken()
        self.writer.write("</class>\n")

    def compileClassVarDec(self):
        self.writer.write("<classVarDec>\n")
        while self.t.token != ';':
            self.writeToken()
        self.writeToken()
        self.writer.write("</classVarDec>\n")

    def compileSubroutine(self):
        self.writer.write("<subroutineDec>\n")
        self.writeToken(4)
        self.compileParameterList()
        self.writeToken()
        self.writer.write("<subroutineBody>\n")
        self.writeToken()
        while self.t.token == "var":
            self.compileVarDec()
        self.compileStatements()
        self.writeToken()
        self.writer.write("</subroutineBody>\n")
        self.writer.write("</subroutineDec>\n")

    def compileParameterList(self):
        self.writer.write("<parameterList>\n")
        while self.t.token != ')':
            self.writeToken()
        self.writer.write("</parameterList>\n")

    def compileVarDec(self):
        self.writer.write("<varDec>\n")
        while self.t.token != ';':
            self.writeToken()
        self.writeToken()
        self.writer.write("</varDec>\n")

    def compileStatements(self):
        self.writer.write("<statements>\n")
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
        self.writer.write("</statements>\n")

    def compileDo(self):
        self.writer.write("<doStatement>\n")
        self.writeToken(2)
        if self.t.token == '.':
            self.writeToken(2)
        self.writeToken()
        self.compileExpressionList()
        self.writeToken(2)
        self.writer.write("</doStatement>\n")

    def compileLet(self):
        self.writer.write("<letStatement>\n")
        self.writeToken(2)
        if self.t.token == '[':
            self.writeToken()
            self.compileExpression()
            self.writeToken()
        self.writeToken()
        self.compileExpression()
        self.writeToken()
        self.writer.write("</letStatement>\n")

    def compileWhile(self):
        self.writer.write("<whileStatement>\n")
        self.writeToken(2)
        self.compileExpression()
        self.writeToken(2)
        self.compileStatements()
        self.writeToken()
        self.writer.write("</whileStatement>\n")

    def compileIf(self):
        self.writer.write("<ifStatement>\n")
        self.writeToken(2)
        self.compileExpression()
        self.writeToken(2)
        self.compileStatements()
        self.writeToken()
        if self.t.token == "else":
            self.writeToken(2)
            self.compileStatements()
            self.writeToken()
        self.writer.write("</ifStatement>\n")

    def compileReturn(self):
        self.writer.write("<returnStatement>\n")
        self.writeToken()
        if self.t.token != ';':
            self.compileExpression()
        self.writeToken()
        self.writer.write("</returnStatement>\n")

    def compileExpressionList(self):
        self.writer.write("<expressionList>\n")
        if self.t.token != ')':
            self.compileExpression()
        while self.t.token == ',':
            self.writeToken()
            self.compileExpression()
        self.writer.write("</expressionList>\n")

    def compileExpression(self):
        self.writer.write("<expression>\n")
        self.compileTerm()
        if self.t.token in "+-*/&|~<>=":
            self.writeToken()
            self.compileTerm()
        self.writer.write("</expression>\n")

    def compileTerm(self):
        self.writer.write("<term>\n")
        if self.t.token in "~-":
            self.writeToken()
            self.compileTerm()
        elif self.t.token == '(':
            self.writeToken()
            self.compileExpression()
            self.writeToken()
        elif self.t.tokenType != "identifier":
            self.writeToken()
        else:
            self.writeToken()
            if self.t.token == '[':
                self.writeToken()
                self.compileExpression()
                self.writeToken()
            elif self.t.token in "(.":
                if self.t.token == '.':
                    self.writeToken(2)
                self.writeToken()
                self.compileExpressionList()
                self.writeToken()
        self.writer.write("</term>\n")

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
    print "usage: jackanalyzer.py [options] source[.jack]\n\tsourceFile(s) may be file or directory.\noptions:\n\t"
