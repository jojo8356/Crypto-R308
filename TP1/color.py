import sys

class color: 
   COLORS=True
   PURPLE = '\033[95m' 
   CYAN = '\033[96m' 
   DARKCYAN = '\033[36m' 
   BLUE = '\033[94m' 
   GREEN = '\033[92m' 
   YELLOW = '\033[93m' 
   RED = '\033[91m' 
   BOLD = '\033[1m' 
   UNDERLINE = '\033[4m' 
   END = '\033[0m' 

def printUtf8(m):
    sys.stdout.buffer.write(m.encode('utf8'))

def Question(i):
    if(color.COLORS):
        printUtf8(color.YELLOW+color.UNDERLINE+"\nQuestion "+str(i)+"\n"+color.END)
    else:
        print("\nQuestion "+str(i)+"\n")

def Exercice(i):
    if(color.COLORS):
        printUtf8(color.RED+color.BOLD+"\nExercice "+str(i)+"\n"+color.END)
    else:
        printUtf8("\nExercice "+str(i)+"\n")

def Error(m):
    if(color.COLORS):
        printUtf8(color.RED+color.UNDERLINE+"\n "+str(m)+"\n"+color.END)
    else:
        printUtf8("\n "+str(m)+"\n")

