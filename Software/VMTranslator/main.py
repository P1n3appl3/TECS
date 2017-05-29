# VM to ASM translator by Joseph Ryan
import sys
import os
from codeparser import CodeParser
from codewriter import CodeWriter

if len(sys.argv) > 1:
    files = []
    fName = sys.argv[-1].replace('\\', '/')
    if fName.endswith(".vm"):
        files.append(fName)
    else:
        for i in os.listdir(fName):
            if i.endswith(".vm"):
                files.append(fName + '/' + i)
    fName = fName.split('.')[0]
    if "-m" not in sys.argv:
        print "Parsing " + str(len(files)) + " file(s)"
    cw = CodeWriter(fName + '/' + fName)
    if "-b" not in sys.argv:
        cw.writeInit()
    for f in files:
        p = CodeParser(f)
        cw.setFile(f)
        if "-m" not in sys.argv:
            print "Translating " + f.split('/')[-1]
        while p.hasMoreCommands():
            c = p.commandType()
            if "-c" in sys.argv:
                cw.f.write("\n//\t\t\t\t" + p.lines[p.currentLine] + '\n')
            if c == "C_ARITHMETIC":
                cw.writeArithmetic(p.arg1())
            elif c in {"C_PUSH", "C_POP"}:
                cw.writePushPop(c, p.arg1(), p.arg2())
            elif c == "C_LABEL":
                cw.writeLabel(p.arg1())
            elif c == "C_GOTO":
                cw.writeGoto(p.arg1())
            elif c == "C_IF":
                cw.writeIf(p.arg1())
            elif c == "C_FUNCTION":
                cw.writeFunction(p.arg1(), p.arg2())
            elif c == "C_CALL":
                cw.writeCall(p.arg1(), p.arg2())
            elif c == "C_RETURN":
                cw.writeReturn()
            p.advance()
    cw.close()
    if "-l" in sys.argv:
        lineNum = 0
        with open(fName + '/' + fName + ".asm", 'r') as src:
            with open(fName + '/' + fName + ".debug", 'w') as dest:
                for line in src:
                    if not line.startswith('(') and not line.startswith('//') and not line == '\n':
                        dest.write(str(lineNum) + '\t\t')
                        lineNum += 1
                    dest.write(line)
    if "-m" not in sys.argv:
        print "Translation Complete"
else:
    print "usage: vmtranslator.py [options] source[.vm]\n\tsourceFile(s) may be file or directory.\noptions:\n\t-m mutes status messages\n\t-c writes vm commands as comments in .asm file\n\t-b doesn't generate bootstrap code\n\t-l creates source.debug with adjusted line numbers"
