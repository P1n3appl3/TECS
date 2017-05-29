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
