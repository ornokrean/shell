from pathlib import Path
import os

USAGE = "usage: "

COMMAND_PREFIX = "-"

LS_NAME = "ls"

LS_VALID = "at"


class Shell:
    currPath = str(Path.home())
    currCommand = ""

    def pwd(self):
        print(self.currPath)

    ###########################################################################

    def cd(self, arg):
        self.currPath = os.path.join(self.currPath, arg)

    def verifyAddress(self):
        f = Path(self.currPath)
        return f.exists()
        #  check for abs or real: if i have this sub path from this one ok.
        # if i dont so i check from base. otherwise error.

    def checkArgs(self, args, valid, command):
        for arg in args:
            if arg not in valid:
                print(USAGE + command + " [" + COMMAND_PREFIX + "".join(
                    valid) + "]")
                return False
        return True

    def parseArgs(self, args):
        if args[0] == COMMAND_PREFIX:
            args = list(args[1:])
        return args

    def ls(self, args):
        args = self.parseArgs(args)
        if not self.checkArgs(args, LS_VALID, LS_NAME):
            return
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
# s.cd("Desktop/t")
s.ls("qwerty")
