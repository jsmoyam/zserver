#!/usr/bin/python3

import argparse
import cmd2
import datetime
import getpass
import inspect
import os
import pathlib
import pyfiglet
import Pyro4.errors
import Pyro4.naming
import shutil
import signal
import socket
import spurplus
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse

from colorama import Fore, Style
from typing import List
from cmd2 import Statement, categorize

# All module commands must start with this prefix and have this last argument
EXECUTABLE_POPEN = '/bin/bash'
SHELL_COMMAND_PREFIX = 'shell_'
HELP_COMMAND_PREFIX = 'help_'
CATEGORY_METHOD_PREFIX = 'category_'
SHELL_MODE_CONNECTION = 'shell_mode'

CAT_VERSION_MANAGEMENT = 'Version management'
CAT_VARIABLE_MANAGEMENT = 'Variable management'
CAT_TOOLS = 'Tools'

PERSISTENT_HISTORY = '~' + os.sep + '.persistent_history.zshell'
STARTUP_SCRIPT_NAME = '.zshellrc'
STARTUP_SCRIPT = '~' + os.sep + STARTUP_SCRIPT_NAME
ZCTL_NAME = 'zctl.py'
VARIABLE_INSTALL_PATH = 'INSTALL_PATH'
VARIABLE_VERSION_NAME = 'VERSION_NAME'
VARIABLE_GIT_URL = 'GIT_URL'
VARIABLE_VENV_BIN_PATH = 'VENV_BIN_PATH'

# This constant tell that if you write install dev then you will clone master
DEVELOPER_BRANCH = ('dev', 'master')

PID_FILE = tempfile.gettempdir() + os.sep + 'z.pid'

# Port for connecting to pyro name server

parser = argparse.ArgumentParser(description='ZServer controller.')
parser.add_argument('-p', '--port', help='Connecting port to pyro4 name server')
args = vars(parser.parse_args())
PYRO_NS_PORT = 9090 if not args['port'] else args['port']



def statement_class_to_dict(obj):
    # Method that serialize cmd2.Statement class to dictionary. obj.args has a string with arguments separated
    # by spaces: "arg1 arg2 arg3". __class__ key is necessary
    return {
        "__class__": "statement",
        "raw-attribute": obj.args
    }


# Register method in pyro4 for correct serialization
Pyro4.util.SerializerBase.register_class_to_dict(cmd2.Statement, statement_class_to_dict)


class MetaShellClient(type):

    def __new__(cls, name, bases, attrs):
        # Target: create dynamic methods in ShellClient class with this metaclass

        # Create empty variable. After it will be filled
        attrs['shell_methods_name'] = list()

        # First recover all methods from server
        # If it fails, regular behaviour will be executed
        try:
            obj = Pyro4.Proxy("PYRONAME:shell_manager_module@:{}".format(PYRO_NS_PORT))
            Pyro4.naming.type_meta(obj)

            # Recover version from server
            z_version_name = obj.shell_zappversion(None)
            if z_version_name:
                attrs['z_version_name'] = z_version_name
            else:
                attrs['z_version_name'] = ''
        except Pyro4.errors.CommunicationError as e1:
            print('Communication error with server: {}'.format(e1))
            attrs['z_version_name'] = ''
            return super(MetaShellClient, cls).__new__(cls, name, bases, attrs)
        except Pyro4.errors.NamingError as e2:
            print('Cannot communicate with shell_manager_module via RPC naming server - {}'.format(e2))
            attrs['z_version_name'] = ''
            return super(MetaShellClient, cls).__new__(cls, name, bases, attrs)

        all_methods = inspect.getmembers(obj)
        attrs['rpc_object'] = obj

        # Filter only by shell methods
        # methods[x][0] --> method name
        # methods[x][1] --> callable method
        shell_methods_from_server = [tup for tup in all_methods if tup[0].startswith(SHELL_COMMAND_PREFIX)]
        help_methods_from_server = [tup for tup in all_methods if tup[0].startswith(HELP_COMMAND_PREFIX)]
        category_methods_from_server = [tup for tup in all_methods if tup[0].startswith(CATEGORY_METHOD_PREFIX)]

        # Rename method name removing SHELL_COMMAND_PREFIX
        # Also save method names in a list
        shell_methods_name = list()
        shell_methods = list()
        for sm in shell_methods_from_server:
            method_name = sm[0][len(SHELL_COMMAND_PREFIX):]
            method_callable = sm[1]
            shell_methods_name.append(method_name)
            shell_methods.append((method_name, method_callable))

        # Save shell methods name in class
        attrs['shell_methods_name'] = shell_methods_name

        # Append help methods
        help_methods = list()
        for sm in help_methods_from_server:
            method_name = sm[0]
            method_callable = sm[1]
            help_methods.append((method_name, method_callable))

        # Encapsulate RPC method call in function to avoid serialization problems with help method
        def make_function(methods, i):
            def function(self, *args):
                try:
                    out = methods[i][1](args)
                    print(out)
                except Pyro4.errors.CommunicationError as e1:
                    print('Communication error with server, probably server is down: {}'.format(e1))
                except ValueError as e2:
                    if str(e2).startswith('too many values to unpack'):
                        print('Server error. Method [{}] is wrong because it does not assign all the arguments [{}] '
                              '(see call method get_args_from_shell(args))'.format(methods[i][0], args[0].args))
                except Exception as e:
                    print('Server error: {}'.format(e))

            return function

        # Get methods categories in dictionary
        categories = dict()
        for i in range(len(category_methods_from_server)):
            categories = {**categories, **category_methods_from_server[i][1]()}

        # Iterate all methods with index
        for i in range(len(shell_methods)):
            # Create do_ method and assign the new function using category function
            created_method_name = 'do_' + shell_methods[i][0]
            attrs[created_method_name] = make_function(shell_methods, i)
            categorize(attrs[created_method_name], categories.get(shell_methods[i][0], 'Uncategorized'))

        # Iterate all help methods with index
        for i in range(len(help_methods)):
            # Create do_ method and assign the new function
            attrs[help_methods[i][0]] = make_function(help_methods, i)

        return super(MetaShellClient, cls).__new__(cls, name, bases, attrs)


class ShellClient(cmd2.Cmd, metaclass=MetaShellClient):

    def __init__(self, history_file: str, startup_script: str):
        self.startup_script = os.path.expanduser(startup_script)
        self.history_file = os.path.expanduser(history_file)

        super().__init__(persistent_history_file=self.history_file, persistent_history_length=500,
                         startup_script=self.startup_script)

        # Set prompt and intro
        self._set_prompt()
        self.intro = pyfiglet.figlet_format('Z Shell') + '\n' + self.z_version_name

        # Set some properties
        self.hidden_commands.append('py')
        self.hidden_commands.append('pyscript')
        self.default_to_shell = True
        self.register_postparsing_hook(self.pre_command_hook)
        self.editor = 'nano'

        # Set variable store
        self.store = dict()

    def pre_command_hook(self, params: cmd2.plugin.PostparsingData) -> cmd2.plugin.PostparsingData:
        # The statement object created from the user input is available as params.statement

        # Add the last argument connection_mode only for python methods. In this case it is always shell_mode
        # This argument will be another in bluetooth module
        if params.statement.command in self.shell_methods_name:
            new_raw_statement = params.statement.raw + ' ' + SHELL_MODE_CONNECTION
            params.statement = self.statement_parser.parse_command_only(new_raw_statement)

        # Modify params detecting if is python command or shell command
        # It needs to create a new statement, not modify the statement in params
        if params.statement.command not in self.keywords:
            # Modify raw argument adding shell command
            new_raw_statement = 'shell ' + params.statement.raw
            params.statement = self.statement_parser.parse_command_only(new_raw_statement)

        return params

    # It needs to redefine this method for autocompleting bash commands in this shell
    def get_commands_aliases_and_macros_for_completion(self) -> List[str]:
        """Return a list of visible commands, aliases, and macros for tab completion"""
        visible_commands = set(self.get_visible_commands())
        alias_names = set(self.get_alias_names())
        macro_names = set(self.get_macro_names())

        import readline
        text = readline.get_line_buffer().lstrip()
        exe_commands = set(self.get_exes_in_path(text))

        return list(visible_commands | alias_names | macro_names | exe_commands)

    def _set_prompt(self):
        """Set prompt so it displays the current working directory."""
        self.cwd = os.getcwd()
        homedir = os.environ['HOME']

        if self.cwd.startswith(homedir):
            self.cwd = '~' + self.cwd[len(homedir):]

        self.username = getpass.getuser()
        self.hostname = socket.gethostname()

        self.prompt = Style.BRIGHT + Fore.GREEN + '{}@{}'.format(self.username, self.hostname) + \
                        Fore.RED + ' {}'.format(time.strftime("%H:%M:%S")) + \
                        Fore.CYAN + ' {} $ '.format(self.cwd) + \
                        Fore.RESET + Style.RESET_ALL

    def postcmd(self, stop: bool, line: str) -> bool:
        """Hook method executed just after a command dispatch is finished.
        :param stop: if True, the command has indicated the application should exit
        :param line: the command line text for this command
        :return: if this is True, the application will exit after this command and the postloop() will run
        """
        """Override this so prompt always displays cwd."""
        self._set_prompt()
        return stop

    @cmd2.with_argument_list
    def do_cd(self, arglist):
        """Change directory.
    Usage:
        cd <new_dir>
        """
        # Expect 1 argument, the directory to change to
        if not arglist or len(arglist) != 1:
            self.perror("cd requires exactly 1 argument:", traceback_war=False)
            self.do_help('cd')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        # Convert relative paths to absolute paths
        path = os.path.abspath(os.path.expanduser(arglist[0]))

        # Make sure the directory exists, is a directory, and we have read access
        out = ''
        err = None
        data = None
        if not os.path.isdir(path):
            err = '{!r} is not a directory'.format(path)
        elif not os.access(path, os.R_OK):
            err = 'You do not have read access to {!r}'.format(path)
        else:
            try:
                os.chdir(path)
            except Exception as ex:
                err = '{}'.format(ex)
            else:
                out = 'Successfully changed directory to {!r}\n'.format(path)
                self.stdout.write(out)
                data = path

        if err:
            self.perror(err, traceback_war=False)
        self._last_result = cmd2.CommandResult(out, err, data)

    # Enable tab completion for cd command
    def complete_cd(self, text, line, begidx, endidx):
        return self.path_complete(text, line, begidx, endidx, path_filter=os.path.isdir)

    def create_startup_file_if_not_exists(self):
        # If startup_script does not exist, then create it empty
        if not os.path.exists(self.startup_script):
            pathlib.Path(self.startup_script).touch()

    def get_startup_script_as_list(self):
        # Recover all lines of startup script
        lines = list()
        with open(self.startup_script, 'r') as f:
            lines = f.readlines()
        return lines

    def get_timestamp(self):
        return '{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())

    def get_all_tags(self, giturl: str) -> list:
        # Recover last tag from repository
        # git ls-remote --tags giturl | awk '{print $2}' | grep -v '{}' | awk -F"/" '{print $3}' |
        #       sort -n -t. -k1,1 -k2,2 -k3,3

        # If exists, convert username and password to url encoded to build git url
        giturl_new = self.get_git_url_encoded(giturl)

        command = "git ls-remote --tags {} | awk '{{print $2}}' | grep -v '{{}}' | awk -F\"/\" '{{print $3}}' | sort -n -t. -k1,1 -k2,2 -k3,3".format(giturl_new)
        output_without_encoding = subprocess.check_output(command, shell=True)
        output = output_without_encoding.decode('utf-8').strip()
        return output.split('\n') + ['dev']

    def get_last_tag(self, giturl: str) -> str:
        # Recover last tag from repository getting all tags and selecting the last
        all_tags = self.get_all_tags(giturl)
        return all_tags[0]

    def get_git_url_encoded(self, giturl):
        # Convert username and password to url encoded
        giturl_new = giturl
        if giturl.startswith('http'):
            slash_index = giturl.index('//')
            username_index = slash_index + len('//')
            double_point_index = giturl.index(':', username_index)
            last_at_index = giturl.rindex('@')

            username = giturl[username_index:double_point_index]
            password = giturl[double_point_index + len(':'):last_at_index]

            giturl_new = '{}{}:{}{}'.format(
                giturl[0:username_index],
                urllib.parse.quote_plus(username),
                urllib.parse.quote_plus(password),
                giturl[last_at_index:]
            )
        return giturl_new

    def list_files(self, file_or_dir: str) -> list:
        # Returns all files in directory with wildcards
        path = pathlib.Path(file_or_dir).expanduser()
        parts = path.parts[1:] if path.is_absolute() else path.parts
        list_generator = pathlib.Path(path.root).glob(str(pathlib.Path("").joinpath(*parts)))
        return [x.name for x in list_generator]

    def get_pid_from_command(self, command: str) -> int:
        # Recover pid from ps -ef searching for command. Return None if not exists
        ps_command = 'ps -ef | grep -v grep | grep -v {} | grep "{}"'.format(EXECUTABLE_POPEN, command)

        try:
            output = subprocess.check_output(ps_command, shell=True, executable=EXECUTABLE_POPEN)
            return int(output.split()[1].decode('utf-8'))
        except subprocess.CalledProcessError as cpe:
            return None

    def version_exists(self, giturl_raw, version_name):
        # Check if version exist in repository
        all_tags = self.get_all_tags(giturl_raw)
        return version_name in all_tags

    def convert_version_name(self, version_name):
        # If version name is "dev", it is neccesary to convert to the correct branch
        return DEVELOPER_BRANCH[1] if version_name.lower() == DEVELOPER_BRANCH[0] else version_name

    def destination_exists(self, destination: str, ssh_connection: str=None) -> bool:
        # Check if exist file in local or in remote server
        if ssh_connection:
            # ssh_connection --> ssh://username:password@server:port
            url = urllib.parse.urlparse(ssh_connection)
            with spurplus.connect_with_retries(
                    retries=5,
                    hostname=url.hostname,
                    username=url.username,
                    password=url.password if url.password else None,
                    port=url.port if url.port else None
            ) as shell:
                return shell.exists(destination)
        else:
            return os.path.isdir(destination)

    def clone_from_repository(self, giturl, version_name, destination):
        os.system('git clone -b {} --single-branch {} {}'.format(version_name, giturl, destination))

    def escape_string(self, text):
        # Replace slash for backslash and slash
        text_escape = ''
        for c in text:
            new_c = c
            if c == '/':
                new_c = '\/'
            text_escape = text_escape + new_c
        return text_escape

    def find_replace(self, path, text, replacement, first_occurrence=False):
        # Replace text in file
        # grep -rl "/pepe/juan" * | xargs sed -i 's/\/tmp\/venv/\/home\/tmp/g'

        text_escape = self.escape_string(text)
        replacement_escape = self.escape_string(replacement)

        folder_or_file = pathlib.Path(path)

        grep_command = 'grep -rl "{}" {}'.format(text, path)
        if folder_or_file.is_dir():
            grep_command = grep_command + os.sep + '*'

        command = ''
        if first_occurrence:
            command = grep_command + ' | xargs sed -i "0,/{}/{{s/{}/{}/}}"'.format(text_escape, text_escape, replacement_escape)
        else:
            command = grep_command + ' | xargs sed -i "s/{}/{}/g"'.format(text_escape, replacement_escape)

        os.system(command)

    def get_variables_from_startup_script(self, ssh_connection: str) -> dict:
        # Get value of remote variable reading startup script directly

        # ssh_connection --> ssh://username:password@server:port
        url = urllib.parse.urlparse(ssh_connection)
        with spurplus.connect_with_retries(
                retries=5,
                hostname=url.hostname,
                username=url.username,
                password=url.password if url.password else None,
                port=url.port if url.port else None
        ) as shell:
            shell.run(['ls'])
            script = os.sep + 'home' + os.sep + url.username + os.sep + STARTUP_SCRIPT_NAME
            content = shell.read_text(script)
            lines = content.split('\n')

            variables = dict()
            for line in lines:
                if line.startswith('zset'):
                    line_as_list = line.split()
                    variables[line_as_list[1]] = line_as_list[2]

            return variables

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zgetlastversion(self, args):
        """Recover last version from Z server.
    Usage:
        getlastversion
        """

        arglist = args.split()

        # Expect 0 argument
        if len(arglist) != 0:
            self.perror('zgetlastversion requires exactly 0 argument:', traceback_war=False)
            self.do_help('zgetlastversion')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        actual_version_name = self.store.get(VARIABLE_VERSION_NAME, None)
        giturl = self.store.get(VARIABLE_GIT_URL, None)
        self.poutput('Actual version: {}'.format(actual_version_name))
        self.poutput('Last version: {}'.format(self.get_last_tag(giturl)))

    @cmd2.with_category(CAT_TOOLS)
    def do_targz(self, args):
        """Create tar gz file creating directory too if not exists.
    Usage:
        targz source_dir output_filename
        """

        arglist = args.split()

        # Expect 2 argument
        if len(arglist) != 2:
            self.perror('targz requires 2 argument:', traceback_war=False)
            self.do_help('targz')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        source_file_or_dir = os.path.expanduser(arglist[0])
        output_filename = os.path.expanduser(arglist[1])

        # Create output directory if not exists
        complete_path = pathlib.Path(output_filename)
        path = pathlib.Path(os.sep.join(complete_path.parts[0:-1])[1:])
        path.mkdir(parents=True, exist_ok=True)

        # Create path for origin
        origin_path = pathlib.Path(source_file_or_dir)

        # Make tar gz
        with tarfile.open(output_filename, "w:gz") as tar:
            if origin_path.is_dir():
                tar.add(source_file_or_dir, arcname=os.path.basename(source_file_or_dir))
            else:
                files = self.list_files(source_file_or_dir)
                for f in files:
                    tar.add(f)

    @cmd2.with_category(CAT_TOOLS)
    def do_untargz(self, args):
        """Create tar gz file creating directory too if not exists.
    Usage:
        untargz input_filename
        untargz input_filename destination_dir
        """

        arglist = args.split()

        # Expect 1 or 2 argument
        if len(arglist) > 2:
            self.perror('untargz requires 1 or 2 argument:', traceback_war=False)
            self.do_help('untargz')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        input_file = os.path.expanduser(arglist[0])
        destination = '.'

        if len(arglist) == 2:
            destination = os.path.expanduser(arglist[1])

            # Create output directory if not exists
            complete_path = pathlib.Path(destination)
            path = pathlib.Path(os.sep.join(complete_path.parts[0:-1])[1:])
            path.mkdir(parents=True, exist_ok=True)

        # Decompress tar gz file
        with tarfile.open(input_file, "r:gz") as tar:
            tar.extractall(path=destination)

    @cmd2.with_category(CAT_TOOLS)
    def do_timestamp(self, args):
        """Generate timestamp.
    Usage:
        timestamp
        """

        self.poutput(self.get_timestamp())

    @cmd2.with_category(CAT_VARIABLE_MANAGEMENT)
    def do_zset(self, args):
        """Set variable in Z server.
    Usage:
        zset varname value
        zset varname value store -> With the keyword store it saves the variable in startup script
        """

        arglist = args.split()

        # Expect 2 argument
        if not arglist or len(arglist) < 2 or len(arglist) > 3:
            self.perror('zset requires 2 or 3 argument:', traceback_war=False)
            self.do_help('zset')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        # Recover arguments
        key = arglist[0]
        value = arglist[1]
        save = False
        if len(arglist) == 3:
            save = True if arglist[2].lower() == 'store' else False

        # Update dictionary
        self.store.update({key: value})

        # Update startup script is save is set
        if save:
            self.create_startup_file_if_not_exists()
            lines = self.get_startup_script_as_list()

            # Open startup script and add at the beginning this variable
            # Be careful because it is possible that already exists the variable in startup script: delete before write
            with open(self.startup_script, 'w') as f:
                new_command = ['zset {} {}\n'.format(key, value)]

                # Delete variable from lines if it exists
                lines_modified = [line for line in lines if not line.lower().startswith('zset {}'.format(key.lower()))]

                lines_with_new_command = new_command + lines_modified
                f.writelines(lines_with_new_command)
                self.poutput('Variable stored {} = {}'.format(key, value))

    @cmd2.with_category(CAT_VARIABLE_MANAGEMENT)
    def do_zget(self, args):
        """Get variable value in Z server. Return 'NOT SET string if not exists.
    Usage:
        zget
        zget varname
        """

        arglist = args.split()

        # Expect 0 or 1 argument
        if len(arglist) > 1:
            self.perror('zget requires 0 or 1 argument:', traceback_war=False)
            self.do_help('zget')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        if len(arglist) == 0:
            for (key, value) in self.store.items():
                self.poutput('{}: {}'.format(key, value))
        elif len(arglist) == 1:
            key = arglist[0]
            value = self.store.get(key, 'NOT SET')
            self.poutput(value)

    @cmd2.with_category(CAT_VARIABLE_MANAGEMENT)
    def do_zdel(self, args):
        """Delete variable value in Z server.
    Usage:
        zdel varname
        """

        arglist = args.split()

        # Expect 1 argument
        if not arglist or len(arglist) != 1:
            self.perror('zdel requires exactly 1 argument:', traceback_war=False)
            self.do_help('zdel')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        key = arglist[0]

        del self.store[key]
        return

    @cmd2.with_category(CAT_VARIABLE_MANAGEMENT)
    def do_zstorevar(self, args):
        """Store all variables in init script.
    Usage:
        zstorevar
        """

        arglist = args.split()

        # Expect 0 argument
        if len(arglist) != 0:
            self.perror('zstorevar requires exactly 0 argument:', traceback_war=False)
            self.do_help('zstorevar')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        #  Create empty startup script sfile
        self.create_startup_file_if_not_exists()

        # Open init script, delete all zset commands and insert the new zset commands at the beginning
        lines = self.get_startup_script_as_list()

        with open(self.startup_script, 'w') as f:
            lines_without_set = [line for line in lines if not line.lower().startswith('zset')]
            new_set = ['zset {} {}\n'.format(key, value) for key, value in self.store.items()]
            lines_with_new_set = new_set + lines_without_set
            f.writelines(lines_with_new_set)

        return

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zinstall(self, args):
        """Install Z server.
    Usage:
        zinstall destination giturl version_name
        """

        arglist = args.split()

        # Expect 3 argument
        if not arglist or len(arglist) != 3:
            self.perror('zinstall requires exactly 3 argument:', traceback_war=False)
            self.do_help('zinstall')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        # Recover arguments
        destination = arglist[0]
        giturl_raw = arglist[1]
        version_name_arg = arglist[2]

        # If exists, convert username and password to url encoded to build git url
        giturl = self.get_git_url_encoded(giturl_raw)

        # Check if version_name exists
        if not self.version_exists(giturl_raw, version_name_arg):
            self.perror('Version does not exist. Please check it.', traceback_war=False)
            return

        # If version name is "dev", it is neccesary to convert to the correct branch
        version_name = self.convert_version_name(version_name_arg)

        # Check if destination folder exists
        if self.destination_exists(destination):
            self.perror('Destination ifolder exists. Please check it and delete it', traceback_war=False)
            return

        # Clone repository to destination folder
        self.poutput('Installing Z server')
        self.clone_from_repository(giturl, version_name, destination)

        # Create virtual environment and install requirements
        venv_dir = os.path.abspath(destination + os.sep + '..' + os.sep + 'venv')
        bin_dir = os.path.abspath(venv_dir + os.sep + 'bin')
        os.system('python3 -m venv ' + venv_dir)
        os.system(bin_dir + os.sep + 'pip install --no-cache-dir -r ' + destination + os.sep + 'requirements.txt')

        # Set install path and version name variables and store them
        self.do_zset('{} {} store'.format(VARIABLE_INSTALL_PATH, destination))
        self.do_zset('{} {} store'.format(VARIABLE_VERSION_NAME, version_name_arg))
        self.do_zset('{} {} store'.format(VARIABLE_GIT_URL, giturl_raw))
        self.do_zset('{} {} store'.format(VARIABLE_VENV_BIN_PATH, bin_dir))

        self.poutput('Z server installed')

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zupgrade(self, args):
        """Upgrade application.
    Usage:
        zupgrade
        zupgrade version_name
        """

        # Recover install path. git url and version name
        install_path = self.store.get(VARIABLE_INSTALL_PATH, None)
        older_version_name = self.store.get(VARIABLE_VERSION_NAME, None)
        giturl = self.store.get(VARIABLE_GIT_URL, None)

        arglist = args.split()

        # Expect 0 or 1 argument
        if len(arglist) > 1:
            self.perror('zupgrade requires 0 or 1 argument:', traceback_war=False)
            self.do_help('zupgrade')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        if len(arglist) == 0:
            # Recover last version from git:
            version_name = self.get_last_tag(giturl)
            version_name_arg = version_name
        elif len(arglist) == 1:
            version_name_arg = arglist[0]
            version_name = version_name_arg
            if version_name_arg.lower() == DEVELOPER_BRANCH[0]:
                version_name = DEVELOPER_BRANCH[1]


        if install_path and older_version_name and giturl:
            # Stop server
            self.do_zstop(None)

            # Compress actual deployment for backup generating compressed file to backup folder
            backup_folder = install_path + os.sep + '..' + os.sep + 'backup' + os.sep
            filename = '{}-{}.tar.gz'.format(self.get_timestamp(), older_version_name)
            compressed_file = backup_folder + filename
            self.do_targz(install_path + ' ' + compressed_file)

            # Delete installation
            shutil.rmtree(install_path)

            # Install the new version
            self.poutput('Upgrading Z server')
            self.do_zinstall(install_path + ' ' + giturl + ' ' + version_name_arg)

        else:
            self.poutput('No installation folder found')

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zremoteinstall(self, args):
        """Install Z server in remote server.
    Usage:
        zremoteinstall destination giturl version_name sshconnection
        sshconnection --> ssh://username:password@server:port
        """

        arglist = args.split()

        # Expect 3 argument
        if not arglist or len(arglist) != 4:
            self.perror('zremoteinstall requires exactly 4 argument:', traceback_war=False)
            self.do_help('zremoteinstall')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        # Recover arguments
        destination = arglist[0]
        giturl_raw = arglist[1]
        version_name_arg = arglist[2]
        ssh_connection = arglist[3]

        # If exists, convert username and password to url encoded to build git url
        giturl = self.get_git_url_encoded(giturl_raw)

        # Check if version_name exists
        if not self.version_exists(giturl_raw, version_name_arg):
            self.perror('Version does not exist. Please check it.', traceback_war=False)
            return

        # If version name is "dev", it is neccesary to convert to the correct branch
        version_name = self.convert_version_name(version_name_arg)

        # Check if destination folder exists
        if self.destination_exists(destination, ssh_connection):
            self.perror('Destination ifolder exists. Please check it and delete it', traceback_war=False)
            return

        # Define and delete if exists destination_tmp and venv_dir_tmp
        destination_tmp = tempfile.gettempdir() + os.sep + 'install'
        venv_dir_tmp = os.path.abspath(destination_tmp + os.sep + '..' + os.sep + 'venv')

        if self.destination_exists(destination_tmp):
            shutil.rmtree(destination_tmp)
        if self.destination_exists(venv_dir_tmp):
            shutil.rmtree(venv_dir_tmp)

        # Clone repository to temporal destination folder
        self.poutput('Installing Z server')
        self.clone_from_repository(giturl, version_name, destination_tmp)

        # Create virtual environment and install requirements
        bin_dir_tmp = os.path.abspath(venv_dir_tmp + os.sep + 'bin')
        os.system('python3 -m venv ' + venv_dir_tmp)
        os.system(bin_dir_tmp + os.sep + 'pip install --no-cache-dir -r ' + destination_tmp + os.sep +
                  'requirements.txt')

        # Define venv_dir. Define python binary folder
        venv_dir = os.path.abspath(destination + os.sep + '..' + os.sep + 'venv')
        bin_dir = os.path.abspath(venv_dir + os.sep + 'bin')

        # Replace all ocurrences of venv_dir_tmp for the new venv folder in destination
        self.find_replace(bin_dir_tmp, venv_dir_tmp, venv_dir)

        # Replace shebang (#!) for venv python in destination_tmp files
        old_shebang = '#!/usr/bin/python3'
        new_shebang = '#!{}'.format(bin_dir) + os.sep + 'python'
        zctl_path_tmp = destination_tmp + os.sep + ZCTL_NAME
        self.find_replace(zctl_path_tmp, old_shebang, new_shebang, first_occurrence=True)

        # Check operations in remote server
        url = urllib.parse.urlparse(ssh_connection)
        with spurplus.connect_with_retries(
                retries=5,
                hostname=url.hostname,
                username=url.username,
                password=url.password if url.password else None,
                port=url.port if url.port else None
        ) as shell:

            # Delete virtual environment if exist
            if shell.exists(venv_dir):
                shell.remove(venv_dir, recursive=True)

            # Copy temporal virtual environment and temporal installation folder to remote server
            shell.mkdir(remote_path=destination, parents=True, exist_ok=True)
            shell.mkdir(remote_path=venv_dir, parents=True, exist_ok=True)

            self.poutput('Copying Z server')
            shell.sync_to_remote(
                local_path=destination_tmp,
                remote_path=destination,
                delete=spurplus.Delete.BEFORE,
                preserve_permissions=True
            )

            self.poutput('Copying virtual environment')
            shell.sync_to_remote(
                local_path=venv_dir_tmp,
                remote_path=venv_dir,
                delete=spurplus.Delete.BEFORE,
                preserve_permissions=True
            )

            # Set install path and version name variables and store them
            # Execute these commands in remote server
            zctl_path = destination + os.sep + ZCTL_NAME
            command_1 = 'zset {} {} store'.format(VARIABLE_INSTALL_PATH, destination)
            command_2 = 'zset {} {} store'.format(VARIABLE_VERSION_NAME, version_name_arg)
            command_3 = 'zset {} {} store'.format(VARIABLE_GIT_URL, giturl_raw)
            command_4 = 'zset {} {} store'.format(VARIABLE_VENV_BIN_PATH, bin_dir)
            command_5 = 'quit'
            zcommand = '{} {} {} {} {}'.format(command_1, command_2, command_3, command_4, command_5)

            chmod_command = ['chmod'] + ['+x'] + [zctl_path]
            command = [zctl_path] + [command_1] + [command_2] + [command_3] + [command_4] + [command_5]
            shell.run(chmod_command)
            shell.run(command)

        self.poutput('Z server installed')

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zremoteupgrade(self, args):
        """Upgrade Z server in remote server.
     Usage:
         zremoteupgrade sshconnection
         zremoteupgrade sshconnection version_name
         sshconnection --> ssh://username:password@server:port
         """

        arglist = args.split()

        # Expect 0 or 1 argument
        if len(arglist) < 1 or len(arglist) > 2:
            self.perror('zremoteupgrade requires 1 or 2 argument:', traceback_war=False)
            self.do_help('zremoteupgrade')
            self._last_result = cmd2.CommandResult('', 'Bad arguments')
            return

        # Recover sshconnection
        ssh_connection = arglist[0]

        # Recover install path. git url and version name
        remote_variables = self.get_variables_from_startup_script(ssh_connection)
        install_path = remote_variables.get(VARIABLE_INSTALL_PATH, None)
        older_version_name = remote_variables.get(VARIABLE_VERSION_NAME, None)
        giturl = remote_variables.get(VARIABLE_GIT_URL, None)

        if len(arglist) == 2:
            version_name_arg = arglist[1]
        else:
            version_name_arg = self.get_last_tag(giturl)

        # Convert version_name is dev is selected
        version_name = version_name_arg
        if version_name_arg.lower() == DEVELOPER_BRANCH[0]:
            version_name = DEVELOPER_BRANCH[1]

        if install_path and older_version_name and giturl:

            # Do some actions in remote server: stop, backup, delete and install

            # ssh_connection --> ssh://username:password@server:port
            url = urllib.parse.urlparse(ssh_connection)
            with spurplus.connect_with_retries(
                    retries=5,
                    hostname=url.hostname,
                    username=url.username,
                    password=url.password if url.password else None,
                    port=url.port if url.port else None
            ) as shell:

                # Stop server
                zctl_path = install_path + os.sep + ZCTL_NAME
                command = [zctl_path] + ['zstop'] + ['quit']
                shell.run(command)

                # Compress actual deployment for backup generating compressed file to backup folder
                backup_folder = install_path + os.sep + '..' + os.sep + 'backup' + os.sep
                filename = '{}-{}.tar.gz'.format(self.get_timestamp(), older_version_name)
                compressed_file = backup_folder + filename

                # Execute targz command
                command = [zctl_path] + ['targz {} {}'.format(install_path, compressed_file)] + ['quit']
                shell.run(command)

                # Delete installation
                command = ['rm'] + ['-rf'] + [install_path]
                shell.run(command)

                # Install the new version
                self.poutput('Upgrading Z server')
                self.do_zremoteinstall(install_path + ' ' + giturl + ' ' + version_name_arg + ' ' + ssh_connection)

        else:
            self.poutput('No installation folder found')

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zstart(self, args):
        """Start Z server.
    Usage:
        zstart
        """

        # Recover install path and python binary variables
        install_path = self.store.get(VARIABLE_INSTALL_PATH, None)
        main_file_path = install_path + os.sep + 'common' + os.sep + 'main.py'
        python_binary_path = self.store.get(VARIABLE_VENV_BIN_PATH, None) + os.sep + 'python'

        if not install_path:
            self.perror('Installation not detected')
        elif not python_binary_path:
            self.perror('Virtual environment not detected')

        # Check if exists pid file. If exists then return
        if os.path.exists(PID_FILE):
            pid = None
            with open(PID_FILE, 'r') as f:
                pid = f.readline()
            if len(pid) > 0 and os.path.exists('/proc/{}'.format(pid)):
                self.perror('Z server is already running')
                return
            else:
                # Delete pid file. There was an error and pid file was not deleted before
                os.remove(PID_FILE)

        # Execute z framework and recover pid
        main_command = python_binary_path + ' ' + main_file_path
        command = 'cd ' + install_path + '; export PYTHONPATH=$PYTHONPATH:' + install_path + '; ' + main_command
        subprocess.Popen(command, shell=True, executable=EXECUTABLE_POPEN, stdout=None, stderr=None)
        main_pid = self.get_pid_from_command(python_binary_path)

        # Create pid file
        with open(PID_FILE, 'w') as f:
            f.write(str(main_pid))

        self.poutput('Z server is running')

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zstop(self, args):
        """Stop Z server.
    Usage:
        zstop
        """

        # Check if pid file exists and recover pid
        if os.path.exists(PID_FILE):
            pid = None
            with open(PID_FILE, 'r') as f:
                pid = f.readline().strip()
            if len(pid) > 0 and os.path.exists('/proc/{}'.format(pid)):
                # Stop server
                os.kill(int(pid), signal.SIGKILL)
                self.poutput('Z server stopped')
            else:
                # Delete pid file. There was an error and pid file was not deleted before
                self.poutput('Z server is not running but pid file is detected. Removed pid file.')

            os.remove(PID_FILE)
        else:
            self.poutput('ZServer is not running')

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zrestart(self, args):
        """Restart Z server.
    Usage:
        zrestart
        """
        self.do_zstop(None)
        time.sleep(1)
        self.do_zstart(None)

    @cmd2.with_category(CAT_VERSION_MANAGEMENT)
    def do_zstatus(self, args):
        """Get status of Z server.
    Usage:
        zstatus
        """

        # Get virtual environment variable
        venv_bin_path = self.store.get(VARIABLE_VENV_BIN_PATH, None)
        if venv_bin_path:
            python_binary_path = venv_bin_path + os.sep + 'python'
        else:
            self.perror('Virtual environment not detected')
            return

        # Check install path variable
        install_path = self.store.get(VARIABLE_INSTALL_PATH, None)
        if not install_path:
            self.perror('Virtual environment not detected')
            return

        # Check if pid file exists and recover pid
        if os.path.exists(PID_FILE):
            pid = None
            with open(PID_FILE, 'r') as f:
                pid = f.readline().strip()
            if len(pid) > 0 and os.path.exists('/proc/{}'.format(pid)):
                ps_pid = self.get_pid_from_command(python_binary_path)
                if ps_pid == int(pid):
                    self.poutput('Z server is running')
                else:
                    self.poutput('Z server is inconsistent. PID from file and from ps are different. Please kill '
                                 'manually and delete pid file in {}'.format(PID_FILE))
            else:
                # Delete pid file. There was an error and pid file was not deleted before
                self.poutput('Z server is not running but pid file is detected. Removed pid file.')
        else:
            main_pid = self.get_pid_from_command(python_binary_path)
            if main_pid:
                # Create pid file with pid from process
                with open(PID_FILE, 'w') as f:
                    f.write(str(main_pid))
            else:
                # Z server is not running
                self.poutput('Z server is not running')


if __name__ == '__main__':
    client = ShellClient(history_file=PERSISTENT_HISTORY, startup_script=STARTUP_SCRIPT)
    client.cmdloop()
