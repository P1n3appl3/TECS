# JACK syntax analyzer by Joseph Ryan
import sys
import os

class Tokenizer:
    line = "\n"
    token = ""
    tokenType = ""
    symbols = "{}()[].,;+-*/&|<>="
    keywords = ["do", "if", "var", "int", "let", "null", "this", "else", "char", "true", "void", "class", "field", "false", "while", "static", "return", "method", "boolean", "function", "constructor"]

    def __init__(self, fileName):
        self.reader = open(fileName)
        self.line = self.reader.readline().lstrip(' ')

    def getToken(self):
        return self.tokenType, self.token

    def advance(self):
        self.line = self.line.lstrip(' ')
        while True:
            if self.line == "\n" or self.line[:2] == "//":      #skip single line comments and empty lines
                self.line = self.reader.readline().lstrip(' ')
            elif self.line[:2] == "/*":     #skip everything until end of block/api comment is found
                while "*/" not in self.line:
                    self.line = self.reader.readline().lstrip(' ')
                self.line = self.line[self.line.find("*/")+2:]
            elif self.line == "":       #readline() only reads empty string at EOF
                return False
            else:
                if self.line[0].isdigit():      #numeric constant
                    i=1
                    while self.line[i].isdigit():
                        i+=1
                    self.tokenType = "integerConstant"
                    self.token = self.line[:i]
                    self.line = self.line[i:]
                elif self.line[0] in self.symbols:      #symbol
                    self.tokenType = "symbol"
                    self.token = self.line[0]
                    self.line = self.line[1:]
                elif self.line[0] == '"':       #string constant
                    self.tokenType = "stringConstant"
                    self.token = self.line.split('"')[1]
                    self.line = '"'.join(self.line.split('"')[2:])
                else:
                    for i in range(2,max(len(self.line), 11)):        #keywords
                        if self.line[:i] in self.keywords:
                            self.tokenType = "keyword"
                            self.token = self.line[:i]
                            self.line = self.line[i:]
                            return True
                    i=1         #identifiers
                    while self.line[i].isalnum() or self.line[i]=='_':
                        i+=1
                    self.tokenType = "identifier"
                    self.token = self.line[:i]
                    self.line = self.line[i:]
                return True

    def __del__(self):
        self.reader.close()

class CompilationEngine:

    def __init__(self):
        pass

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
        t = Tokenizer(f)
        while t.advance():
            print t.getToken()
else:
    print "usage: jackanalyzer.py [options] source[.jack]\n\tsourceFile(s) may be file or directory.\noptions:\n\t"
