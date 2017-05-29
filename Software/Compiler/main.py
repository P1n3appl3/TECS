# JACK to VM compiler by Joseph Ryan
import sys
import os
from compilationengine import CompilationEngine

if len(sys.argv) > 1:
    files = []
    fName = sys.argv[-1].replace('\\', '/')
    if fName.endswith(".jack"):
        files.append(fName)
    else:
        for i in os.listdir(fName):
            if i.endswith(".jack"):
                files.append(fName + '/' + i)
    if "-m" not in sys.argv:
        print "Parsing " + str(len(files)) + " file(s)"
    for f in files:
        if "-m" not in sys.argv:
            print "Compiling " + f.split('/')[-1]
        c = CompilationEngine(f)
        c.compileClass()
    if "-m" not in sys.argv:
        print "Compilation Complete"
else:
    print "usage: compiler.py [options] source[.jack]\n\tsourceFile(s) may be file or directory.\noptions:\n\t-m mutes status messages\n\t-x creates syntax analysis xml file"
