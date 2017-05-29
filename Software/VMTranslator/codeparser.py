# Handles input parsing and sanatization
class CodeParser:
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
