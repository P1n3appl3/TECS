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
            if self.line[:i] in self.keywords and not self.line[i].isalpha():
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

    def nextToken(self):
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
        if not self.nextToken():
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
