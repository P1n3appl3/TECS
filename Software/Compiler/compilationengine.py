import sys
from symboltable import SymbolTable
from tokenizer import Tokenizer
from vmwriter import VMWriter


class CompilationEngine:

    def __init__(self, fileName):
        if '-x' in sys.argv:
            self.writer = open(fileName.split('.')[0] + ".xml", 'w')
        self.t = Tokenizer(fileName)
        self.t.advance()
        self.vm = VMWriter(fileName)
        self.table = None
        self.classTable = SymbolTable()
        self.fieldCount = 0

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
        kind = self.t.token
        self.writeToken()
        type = self.t.token
        self.writeToken()
        while self.t.token != ';':
            if self.t.token != ',':
                self.classTable.add(self.t.token, type, kind)
                if kind == "field":
                    self.fieldCount += 1
            self.writeToken()
        self.writeToken()
        self.writeXML("</classVarDec>")

    def compileSubroutine(self):
        self.writeXML("<subroutineDec>")
        self.whileCount = 0
        self.ifCount = 0
        self.table = SymbolTable()
        self.functionKind = self.t.token
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
        if self.functionKind == "constructor":
            self.vm.writePush("constant", self.fieldCount)
            self.vm.writeCall("Memory.alloc", 1)
            self.vm.writePop("pointer", 0)
        elif self.functionKind == "method":
            self.vm.writePush("argument", 0)
            self.vm.writePop("pointer", 0)
        self.compileStatements()
        self.writeToken()
        self.writeXML("</subroutineBody>")
        self.writeXML("</subroutineDec>")

    def compileParameterList(self):
        self.writeXML("<parameterList>")
        if self.functionKind == "method":   # add empty argument for self
            self.table.add('', self.className, "argument")
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
        self.compileCall(name)
        self.writeToken()
        self.vm.writePop("temp", 0)
        self.writeXML("</doStatement>")

    def compileLet(self):
        self.writeXML("<letStatement>")
        self.writeToken()
        name = self.t.token
        self.writeToken()
        temp = False
        if self.t.token == '[':
            self.compileArray(name)
            temp = True
        self.writeToken()
        self.compileExpression()
        self.writeToken()
        t = self.table
        if not t.has(name):
            t = self.classTable
        if temp:
            self.vm.writePop("temp", 0)
            self.vm.writePop("pointer", 1)
            self.vm.writePush("temp", 0)
            self.vm.writePop("that", 0)
        else:
            self.vm.writePop(t.getKind(name), t.getCount(name))
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
        if self.t.token == "else":
            self.vm.writeGoto("IF_END" + str(currentCount))
            self.vm.writeLabel("IF_FALSE" + str(currentCount))
            self.writeToken(2)
            self.compileStatements()
            self.writeToken()
            self.vm.writeLabel("IF_END" + str(currentCount))
        else:
            self.vm.writeLabel("IF_FALSE" + str(currentCount))
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

    def compileCall(self, name):    # starts with tokenizer after the function name
        argNum = 0
        if self.t.token == '.':  # not a local method
            self.writeToken()
            t = self.table
            if not t.has(name):  # not a local object's method
                t = self.classTable
            if t.has(name):  # must be a local or field object's method
                self.vm.writePush(t.getKind(name), t.getCount(name))
                name = t.getType(name) + '.' + self.t.token
                argNum = 1
            else:   # must be an external function
                name += '.' + self.t.token
            self.writeToken()
        else:   # local method
            self.vm.writePush("pointer", 0)
            name = self.className + '.' + name
            argNum = 1
        self.writeToken()
        argNum += self.compileExpressionList()
        self.writeToken()
        self.vm.writeCall(name, argNum)

    def compileArray(self, name):   # starts with tokenizer after the array name
        t = self.table
        if not t.has(name):
            t = self.classTable
        self.writeToken()
        self.compileExpression()
        self.writeToken()
        self.vm.writePush(t.getKind(name), t.getCount(name))
        self.vm.writeArithmetic('+')

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
        while self.t.token in "+-*/%&|~<>=":
            op = self.t.token
            self.writeToken()
            self.compileTerm()
            self.vm.writeArithmetic(op)
        self.writeXML("</expression>")

    def compileTerm(self):
        self.writeXML("<term>")
        if self.t.tokenType == "stringConstant":
            self.vm.writePush("constant", len(self.t.token))
            self.vm.writeCall("String.new", 1)
            for i in self.t.token:
                self.vm.writePush("constant", ord(i))
                self.vm.writeCall("String.appendChar", 2)
            self.writeToken()
        elif self.t.token in "~-" and self.t.token != '':
            op = self.t.token
            self.writeToken()
            self.compileTerm()
            self.vm.writeUnary(op)
        elif self.t.token == '(':
            self.writeToken()
            self.compileExpression()
            self.writeToken()
        elif self.t.tokenType == "identifier":
            name = self.t.token
            self.writeToken()
            if self.t.token == '[':  # array
                self.compileArray(name)
                self.vm.writePop("pointer", 1)
                self.vm.writePush("that", 0)
            elif self.t.token in "(.":  # function
                self.compileCall(name)
            else:   # normal variable/object
                t = self.table
                if not t.has(name):
                    t = self.classTable
                self.vm.writePush(t.getKind(name), t.getCount(name))
        else:
            if self.t.tokenType == "integerConstant":
                self.vm.writePush("constant", self.t.token)
            elif self.t.tokenType == "keyword":  # this/null/false/true
                if self.t.token == "this":
                    self.vm.writePush("pointer", 0)
                else:
                    self.vm.writePush("constant", 0)
                    if self.t.token == "true":
                        self.vm.writeUnary('~')
            self.writeToken()
        self.writeXML("</term>")
