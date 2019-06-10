import socket
from pathlib import Path
import os
import shutil

COPY_TO_FILE = ": can't copy into a file"

"""
Class Shell, has two fields:
    currPath - for the current path we are in
    homePath - for the os home path
And the following main functions:
    cd [dir] - directory could be relative or full path

    pwd

    ls [-at]  - "a" flag means to display hidden files and "t" means to 
                sort by file/directory creation time

    cp [-r] source dest - "r" means to copy source directory recursively
"""


class Shell:
    # ========= Command Names =========
    CP_NAME = "cp"
    CD_NAME = "cd"
    PWD_NAME = "pwd"
    LS_NAME = "ls"

    # ========= Functions Arguments =========
    RECURSIVE_COPY = "r"
    CP_VALID = RECURSIVE_COPY

    CREATION_OREDR_FILES = "t"
    ALL_FILES = "a"
    LS_VALID = ALL_FILES + CREATION_OREDR_FILES

    # ========= Messages and symbols =========
    USAGE = "usage: "
    INVALID_SHELL_USAGE = ": command not found. usage: cd [dir] | pwd | ls " \
                          "[-at] | cp [-r]"
    COMMAND_PREFIX = "-"
    HIDDEN_PREFIX = '.'
    WINDOWS_SEPARATOR = "\\"
    UNIX_SEPARATOR = "/"
    EMPTY_STR = ""
    CD_TO_PARENT = ".."
    CP_MSG = "cp: "
    NO_FILE_OR_DIR = ": No such file or directory"

    # ========= Member Fields =========
    currPath = str(Path.home())
    homePath = str(Path.home())

    # ========= Functions =========

    """
       This is the cd [dir] - Change directory function, it changes the 
       directory to given path.
       If it's given ".." it goes up to the parent, if it's given "" or None 
       it will return to home directory.
       other wise it will try to change to the given path: if it is absolute 
       path it will go there only is it is an existing directory, otherwise it 
       will join it to the current path and will go there only is it is an 
       existing directory. if it is not an existing directory, it will print 
       error.
       """

    def cd(self, arg=None):
        # act like "cd " command, go home.
        if arg is None or arg == [] or arg[0] == Shell.EMPTY_STR:
            self.currPath = self.homePath
            return

        addr = arg[0]

        # act like "cd .." command, go to parent.
        if addr == Shell.CD_TO_PARENT:
            p = Path(self.currPath)
            self.currPath = str(p.parent)
            return

        # get a normalized and absolute path
        path_verify, new_path = self.parse_and_verify_path(addr)
        if path_verify:
            self.currPath = new_path
        else:
            # print the right message:
            if not os.path.exists(new_path):
                error = "No such file or directory"
            else:
                error = "Not a directory"
            print("cd: " + addr + ": " + error)

    """
    This is the pwd -  Print working directory function. It will print the 
    current working directory.
    """

    def pwd(self, args):
        print(self.currPath)

    """
    This is the ls [-at] - List directory function. It will print all the 
    files in current path, and can take two values: "a" flag means to 
    display hidden files and "t" means to sort by file/directory creation 
    time.
    """

    def ls(self, args):
        # Check all args:
        # check if args is of the form "-XX"
        for arg in args:
            if len(arg) != 0:
                if arg[0] == "-":
                    # check if all args after "-"  are valid
                    if not self.check_args(arg[1:], Shell.LS_VALID,
                                           Shell.LS_NAME):
                        return
                else:
                    print(Shell.USAGE + Shell.LS_NAME + " [" +
                          Shell.COMMAND_PREFIX + "".join(
                        Shell.LS_VALID) + "]")
                    return

        args = set("".join([i.replace("-", "") for i in args]))

        # Get all files from directory
        files = self.get_files(args)

        # Order files by creation time if needed:
        if Shell.CREATION_OREDR_FILES in args:
            files = self.order_by_creation_time(files)

        # Print out the files list:
        self.print_files(files)

    """
    This is the cp [-r] source dest - Copy function. It will copy all the 
    files in current path to the destination, and can take a value: "r" 
    means to copy source directory recursively
    """

    def cp(self, args):
        # Check and assign args:
        if args[0] == Shell.COMMAND_PREFIX + Shell.RECURSIVE_COPY and len(
                args) >= 3:
            recursive_cpy, source, dest = True, args[1], args[2]
        elif len(args) >= 2:
            recursive_cpy, source, dest = False, args[0], args[1]
        else:
            print(Shell.USAGE + Shell.CP_NAME + " [" + Shell.COMMAND_PREFIX +
                  Shell.CP_VALID + "] source dest")
            return

        # check source and dest
        valid, source, dest = self.valid_src_and_dst(source, dest)
        if valid:
            self.copy_files(source, dest, recursive_cpy)

    # =========  Auxiliary functions =========

    # ========= Functions for ls =========
    """
    This function prints all the files given
    """

    def print_files(self, files):
        for file in files:
            print(file)

    """
    This function gets all the files from currPath.
    if there is a "a" flag in args it will take the hidden files too.
    """

    def get_files(self, args):
        if Shell.ALL_FILES in args:
            # Get hidden files:
            files = [f for f in os.listdir(self.currPath)]
        else:
            # Get all but hidden files:
            files = [f for f in os.listdir(self.currPath) if not
            f.startswith(Shell.HIDDEN_PREFIX)]
        return files

    """
    This function orders the given files list by creation time and returns it.
    """

    def order_by_creation_time(self, files):
        mtime = lambda f: os.stat(os.path.join(self.currPath, f)).st_mtime
        files = list(sorted(files, key=mtime))
        return files

    # ========= Functions for cp =========

    """
    This functions parses a new source and destination path and check if
    they are existing directories. 
    returns a tuple of: (Valid - Boolean, newSource - absolute path, 
    newDest - absolute path) or False if either invalid.
    """

    def valid_src_and_dst(self, source, dest):

        verify_src, new_src = self.parse_and_verify_path(source)
        if not os.path.exists(new_src):
            print(Shell.CP_MSG + source + Shell.NO_FILE_OR_DIR)
            return False, None, None

        verify_dest, new_dest = self.parse_and_verify_path(dest)
        if not verify_dest:
            print(Shell.CP_MSG + dest + Shell.NO_FILE_OR_DIR)
            return False, None, None

        if os.path.isfile(dest):
            print(Shell.CP_MSG + dest + COPY_TO_FILE)
            return False, None, None

        return True, new_src, new_dest

    """
    This function copies all the files from source to dest, and if 
    recursive_cpy is true it will copy recursively
    """

    def copy_files(self, source, dest, recursive_cpy):
        if recursive_cpy and os.path.isdir(source):
            self.copytree(source, dest)
        else:
            # copy regularly
            if os.path.isdir(source):
                print("cp: " + source + " is a directory (not copied).")
                return
            shutil.copy(source, dest)

    """
    This is an external function that copies files from source to dest, 
    i will use it in cp function
    """

    def copytree(self, src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

    # ======== Functions for path parsing and argument validation ========

    """
    This functions parses a new absolute path and check if it is an 
    existing directory. 
    returns a tuple of: (Valid - Boolean, newPath - absolute path)
    """

    def parse_and_verify_path(self, path):
        # normalize the path if needed
        new_path = os.path.normpath(path)
        # add the path to current path
        new_path = os.path.join(self.currPath, new_path)
        return os.path.exists(new_path) and os.path.isdir(new_path), new_path

    """
    This function checks the if all of the given args are in the valid 
    args, else will print usade command with the calling_function as the 
    function name.
    """

    def check_args(self, args, valid, calling_function):
        for arg in args:
            if arg not in valid:
                print(Shell.USAGE + calling_function + " [" +
                      Shell.COMMAND_PREFIX + "".join(valid) + "]")
                return False
        return True

    """
    This function run the shell program
    """
    def runShell(self):
        shell_commands = {Shell.CP_NAME: Shell.cp, Shell.LS_NAME: Shell.ls,
                          Shell.PWD_NAME: Shell.pwd, Shell.CD_NAME: Shell.cd}
        while True:
            # get input
            cmd = input(socket.gethostname() + ": " + self.currPath + "$ ")

            # split the input into list of non empty strings:
            cmd_args = list(filter(None, cmd.split(" ")))

            # check for invalid function name
            if cmd_args[0] not in shell_commands:
                print(cmd_args[0] + Shell.INVALID_SHELL_USAGE)
                continue

            # run the current command
            shell_commands[cmd_args[0]](self, cmd_args[1:])


def main():
    shell = Shell()
    shell.runShell()


if __name__ == '__main__':
    main()
