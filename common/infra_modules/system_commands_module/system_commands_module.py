import fabric
import fnmatch
import math
import os
import pathlib
import re
import subprocess
import threading
import urllib

from common import config
from common.app_model import GenericErrorMessages

from common.infra_modules.infra_module import InfraModule
from common.infra_tools.decorators import log_function

from common.infra_modules.system_commands_module import MODULE_NAME

logger = config.get_log(MODULE_NAME)


class SystemCommandsModule(InfraModule):

    # Command list
    VISIBLE_BLUETOOTH = 'hciconfig hci0 piscan'
    SHUTDOWN = 'shutdown -h {}'
    USED_SPACE = 'df -h --output=target,pcent'
    CONSUMED_RAM = "free -m | awk 'NR==2{{printf \"%.2f%%\\t\\t\", $3*100/$2 }}'"
    CPU_LOAD = "percent=$(cat /proc/loadavg | awk '{{print$1}}'); cores=$(nproc); getCpuLoadOutput=$(echo \"scale=2; 100*$percent/$cores\" | bc); echo $getCpuLoadOutput"
    PROCESS_LIST = 'ps cax'

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """

    def execute_command(command: str, sudo=False, host='localhost', user=None, password=None, port=None, execute_in_thread=False):
        """
        Execute shell command in local or remote server
        :param sudo: True/False, execute as sudo
        :param host: host in which execute command
        :param user: ssh username
        :param password: ssh password
        :param port: ssh port
        :return: stdout and stderr in tuple, (None, None) if error
        """

        def execute_command_wrapper(command: str, sudo=False, host='localhost', user=None, password=None, port=None):
            regexp = '^localhost$|^127(?:\.[0-9]+){0,2}\.[0-9]+$|^(?:0*\:)*?:?0*1$'
            is_localhost = bool(re.search(regexp, host))

            # Create fabric connection
            try:
                if is_localhost:
                    conn = fabric.Connection(host)
                    modified_command = 'sudo ' + command if sudo else command
                    output = conn.local(modified_command)
                else:
                    conn = fabric.Connection(host, user=user, port=port)
                    if password and len(password) > 0:
                        conn.connect_kwargs.look_for_keys = False
                        conn.connect_kwargs.password = password
                        conn.connect_kwargs.allow_agent = False
                    output = conn.sudo(command) if sudo else conn.run(command)

                return output.stdout, output.stderr
            except Exception:
                logger.error(GenericErrorMessages.EXECUTED_COMMAND_ERROR, exc_info=True)
                return None, None

        if execute_in_thread:
            t = threading.Thread(target=execute_command_wrapper, args=(command, sudo, host, user, password, port))
            t.setDaemon(True)
            t.start()
        else:
            return execute_command_wrapper(command, sudo=sudo, host=host, user=user, password=password, port=port)

    @log_function(logger)
    def set_bluetooth_visible(self, host='localhost', user='', port=22, password='') -> bool:
        """Set bluetooth visible. Return if execution was correct"""
        stdout, stderr = SystemCommandsModule.execute_command(SystemCommandsModule.VISIBLE_BLUETOOTH, sudo=True,
                                                              host=host, user=user, port=port, password=password)
        if stdout and stderr:
            return len(stdout) == 0 and len(stderr) == 0
        else:
            return False

    @log_function(logger)
    def shutdown(when: str, host='localhost', user='', port=22) -> None:
        """Shutdown system when arguments say"""
        stdout, stderr = SystemCommandsModule.execute_command(SystemCommandsModule.SHUTDOWN.format(when), sudo=True,
                                                              host=host, user=user, port=port)
        if stdout and stderr:
            return len(stdout) == 0 and len(stderr) == 0
        else:
            return False

    def get_git_url_encoded(giturl):
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

    @log_function(logger)
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

    def list_files(file_or_dir: str) -> list:
        # Returns all files in directory with wildcards
        path = pathlib.Path(file_or_dir).expanduser()
        parts = path.parts[1:] if path.is_absolute() else path.parts
        list_generator = pathlib.Path(path.root).glob(str(pathlib.Path("").joinpath(*parts)))
        return [x.name for x in list_generator]

    def clone_from_repository(giturl, version_name, destination):
        os.system('git clone -b {} --single-branch {} {}'.format(version_name, giturl, destination))

    def escape_string(text):
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
            command = grep_command + ' | xargs sed -i "0,/{}/{{s/{}/{}/}}"'.format(text_escape, text_escape,
                                                                                   replacement_escape)
        else:
            command = grep_command + ' | xargs sed -i "s/{}/{}/g"'.format(text_escape, replacement_escape)

        os.system(command)

    def used_space_percent(mount_point: str, host='localhost', user='', password='', port=22) -> int:
        """
        Return used space percent in mount point
        :param mount_point: mount point to examine
        :param host: data for ssh connection
        :param user: data for ssh connection
        :param password: data for ssh connection
        :param port: data for ssh connection
        :return: used space percent as int upper round
        """

        stdout, stderr = SystemCommandsModule.execute_command(SystemCommandsModule.USED_SPACE, sudo=False,
                                                              host=host, user=user, port=port, password=password)

        # df return string with \n
        lines = stdout.split('\n')
        for line in lines:
            # Delete intermediate spaces and split to obtain mount_point and used space percent
            line_without_spaces = re.sub(' +', ' ', line).strip()
            subline = line_without_spaces.split(' ')
            folder = subline[0]

            if folder == mount_point:
                used_space = int(subline[1][0:-1])
                return used_space

        return None

    def check_used_space_percent(mount_point_wildcard: str, value: int, host='localhost', user='', password='', port=22) -> int:
        """
        Return first mount point in which used space is greather than value
        :param mount_point_wildcard: mount point to examine
        :param value: value to check. If greater than return True
        :param host: data for ssh connection
        :param user: data for ssh connection
        :param password: data for ssh connection
        :param port: data for ssh connection
        :return: folder if used space percent is greater than value, else None
        """

        stdout, stderr = SystemCommandsModule.execute_command(SystemCommandsModule.USED_SPACE, sudo=False,
                                                              host=host, user=user, port=port, password=password)

        value_int = int(value)

        # df return string with \n
        lines = stdout.split('\n')
        for line in lines:
            # Delete intermediate spaces and split to obtain mount_point and used space percent
            line_without_spaces = re.sub(' +', ' ', line).strip()
            subline = line_without_spaces.split(' ')
            folder = subline[0]

            if fnmatch.fnmatch(folder, mount_point_wildcard):
                used_space = int(subline[1][0:-1])
                if used_space > value_int:
                    return folder

        return None

    def consumed_ram_percent(host='localhost', user='', password='', port=22) -> int:
        """
        Returns consumed ram percentage
        :param host: data for ssh connection
        :param user: data for ssh connection
        :param password: data for ssh connection
        :param port: data for ssh connection
        :return: int without decimals
        """

        stdout, stderr = SystemCommandsModule.execute_command(SystemCommandsModule.CONSUMED_RAM, sudo=False,
                                                              host=host, user=user, port=port, password=password)
        return math.ceil(float(stdout.split('%')[0]))

    def load_cpu(host='localhost', user='', password='', port=22) -> int:
        """
        Returns cpu load in range 0-100-...
        :param host: data for ssh connection
        :param user: data for ssh connection
        :param password: data for ssh connection
        :param port: data for ssh connection
        :return: cpu load as int without decimals
        """

        stdout, stderr = SystemCommandsModule.execute_command(SystemCommandsModule.CPU_LOAD, sudo=False,
                                                              host=host, user=user, port=port, password=password)
        return math.ceil(float(stdout.strip()))

    def get_process_dict(host='localhost', user='', password='', port=22) -> int:
        """
        Returns dictionary of key pid and value process name
        :param host: data for ssh connection
        :param user: data for ssh connection
        :param password: data for ssh connection
        :param port: data for ssh connection
        :return: process list as dictionary
        """

        stdout, stderr = SystemCommandsModule.execute_command(SystemCommandsModule.PROCESS_LIST, sudo=False,
                                                              host=host, user=user, port=port, password=password)

        # ps return string with \n
        lines = stdout.split('\n')
        process_dict = dict()
        for line in lines:
            # Delete intermediate spaces and split to obtain mount_point and used space percent
            line_without_spaces = re.sub(' +', ' ', line).strip()
            subline = line_without_spaces.split(' ')
            try:
                pid = int(subline[0])
                command = subline[len(subline)-1]
            except ValueError as ve:
                continue

            process_dict[pid] = command

        return process_dict

    def is_process_name_active(process_name: str, host='localhost', user='', password='', port=22) -> int:
        """
        Check if process name is active
        :param process_name: process name
        :param host: data for ssh connection
        :param user: data for ssh connection
        :param password: data for ssh connection
        :param port: data for ssh connection
        :return: True if process name found
        """

        process_dict = SystemCommandsModule.get_process_dict(host=host, user=user, password=password, port=port)
        for pid, name in process_dict.items():
            if name == process_name:
                return True

    def is_process_pid_active(pid: int, host='localhost', user='', password='', port=22) -> int:
        """
        Check if pid process is active
        :param pid: process pid
        :param host: data for ssh connection
        :param user: data for ssh connection
        :param password: data for ssh connection
        :param port: data for ssh connection
        :return: True if pid found
        """

        process_dict = SystemCommandsModule.get_process_dict(host=host, user=user, password=password, port=port)
        return pid in process_dict
