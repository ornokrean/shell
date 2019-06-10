from pathlib import Path
import os

class Shell:
    currPath = str(Path.home())
    currCommand = ""




    def pwd(self):
        print(self.currPath)

#############################################################################

    def cd(self):
        #os.path.join(
        pass

    def verifyAddress(self):
        f = Path(self.currPath)
        return f.exists()
        #  check for abs or rel: if i have this sub path from this one ok.
        # if i dont so i check from base. otherwise error.


    def ls(self,args):
        allFiles = [f for f in os.listdir(self.currPath)  if not
            f.startswith('.')]
        if "a" in args:
            # Get hidden files:
            allFiles = [f for f in os.listdir(self.currPath)]
        if "t" in args:
            # Order by creation time:
            allFiles.sort(key=os.path.getctime)
        for file in allFiles:
            print(file)


    def cp(self, args, source, dest):
        # check source and dest
        # if r, copy recursively
        pass



s = Shell()

s.pwd()
s.ls(["a","t"])


