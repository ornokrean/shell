import socket
from pathlib import Path
import os
import shutil

EMPTY_STR = ""

CD_TO_PARENT = ".."

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
    INVALID_SHELL_USAGE = "Invalid Shell func: usage: cd[dir] | pwd | ls[" \
                          "-at] | cp[-r]"
    COMMAND_PREFIX = "-"
    HIDDEN_PREFIX = '.'
    WINDOWS_SEPARATOR = "\\"
    UNIX_SEPARATOR = "/"

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
        # TODO check all possible outcomes

        # act like "cd " command, go home.
        if arg is None or arg == [] or arg[0] == EMPTY_STR:
            self.currPath = self.homePath
            return

        addr = arg[0]

        # act like "cd .." command, go to parent.
        if addr == CD_TO_PARENT:
            p = Path(self.currPath)
            self.currPath = str(p.parent)
            return

        # get a normalized and absolute address
        address_verify, new_address = self.parse_address(addr)
        if address_verify:
            self.currPath = new_address
        else:
            if not os.path.exists(new_address):
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
        # Convert arg string to array of chars:
        args = "".join(args)

        # check if args is of the form "-XX"
        if len(args) != 0 and args[0] != "-":
            return

        # check if all args after "-"  are valid
        if not self.check_args(args[1:], Shell.LS_VALID, Shell.LS_NAME):
            return

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
        args = "".join(args)

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

        if not self.check_args(args, Shell.CP_VALID, Shell.CP_NAME):
            return

        # check source and dest
        if not self.valid_src_and_dst(source, dest):
            return

        self.copy_files(dest, source, recursive_cpy)

    # =========  Auxiliary functions =========

    # ========= Functions for ls =========

    def print_files(self, files):
        for file in files:
            print(file)

    def get_files(self, args):
        if Shell.ALL_FILES in args:
            # Get hidden files:
            files = [f for f in os.listdir(self.currPath)]
        else:
            # Get all but hidden files:
            files = [f for f in os.listdir(self.currPath) if not
            f.startswith(Shell.HIDDEN_PREFIX)]
        return files

    def order_by_creation_time(self, files):
        mtime = lambda f: os.stat(os.path.join(self.currPath, f)).st_mtime
        files = list(sorted(files, key=mtime))
        return files

    # ========= Functions for cp =========

    def valid_src_and_dst(self, source, dest):
        if not self.verify_address(source)[0]:
            print("cp: " + source + ": No such file or directory")
            return False
        if not self.verify_address(dest)[0]:
            print("cp: " + dest + ": No such file or directory")
            return False
        return True

    def copy_files(self, dest, source, recursive_cpy):
        if recursive_cpy:
            # copy recursively
            try:
                shutil.copytree(source, dest)
            # Directories are the same
            except shutil.Error as e:
                print('Directory not copied. Error: %s' % e)
            # Any error saying that the directory doesn't exist
            except OSError as e:
                print('Directory not copied. Error: %s' % e)
        else:
            # copy regularly
            shutil.copy(source, dest)

    # ======== Functions for address parsing and argument validation ========

    def parse_address(self, arg):
        # normalize the address if needed
        new_address = os.path.normpath(arg)
        # add the address to current path
        new_address = os.path.join(self.currPath, new_address)
        return new_address
    """
    """
    def verify_address(self, path):
        new_path = self.parse_address(path)
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







s = Shell()
while (1):
    shell_commands = {Shell.CP_NAME: Shell.cp, Shell.LS_NAME: Shell.ls,
                      Shell.PWD_NAME:
                          Shell.pwd, Shell.CD_NAME: Shell.cd}
    cmd = input(socket.gethostname() + ": " + s.currPath + "$ ")
    cmd_args = list(filter(None, cmd.split(" ")))

    if cmd_args[0] not in shell_commands:
        print(Shell.INVALID_SHELL_USAGE)
        continue
    shell_commands[cmd_args[0]](s, cmd_args[1:])
