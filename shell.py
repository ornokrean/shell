from pathlib import Path
import os


class Shell:
    currPath = str(Path.home())
    currCommand = ""

    def pwd(self):
        print(self.currPath)

    ###########################################################################

    def cd(self):
        # os.path.join(
        pass

    def verifyAddress(self):
        f = Path(self.currPath)
        return f.exists()
        #  check for abs or rel: if i have this sub path from this one ok.
        # if i dont so i check from base. otherwise error.

    def ls(self, args):
        all_files = [f for f in os.listdir(self.currPath) if not
        f.startswith('.')]
        if "a" in args:
            # Get hidden files:
            all_files = [f for f in os.listdir(self.currPath)]
        if "t" in args:
            # Order by creation time:
            mtime = lambda f: os.stat(os.path.join(self.currPath, f)).st_mtime
            all_files = list(sorted(all_files, key=mtime))
        # all_files.sort(key=os.path.getctime)
        for file in all_files:
            print(file)

    def cp(self, args, source, dest):
        # check source and dest
        # if r, copy recursively
        pass


s = Shell()

s.pwd()
s.ls(["a", "t"])
