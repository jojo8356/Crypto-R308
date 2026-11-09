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


def Question(i):
    if(color.COLORS):
        print(color.YELLOW+color.UNDERLINE+"\nQuestion "+str(i)+"\n"+color.END)
    else:
        print("\nQuestion "+str(i)+"\n")

def Exercice(i):
    if(color.COLORS):
        print(color.RED+color.UNDERLINE+"\nExercice "+str(i)+"\n"+color.END)
    else:
        print("\nExercice "+str(i)+"\n")


