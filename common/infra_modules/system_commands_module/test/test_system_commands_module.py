import time
from nose.tools import assert_equal, assert_true

from common import config
from common.infra_modules.system_commands_module.system_commands_module import SystemCommandsModule


class TestSystemCommandsModule(object):
    module = None

    def __init__(self):
        # Data for ssh connection
        self.ssh_host = 'jsmoya'
        self.ssh_port = 22
        self.ssh_username = 'admuser'
        self.ssh_password = 'marbella2018'

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """

        TestSystemCommandsModule.module = SystemCommandsModule(config, 'system_commands_module')

    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """


    def setup(self):
        """
        This method is run once before _each_ test method is executed
        """

    def teardown(self):
        """
        This method is run once after _each_ test method is executed
        """

    def test_1_execute_command(self) -> None:
        """
        Execute ls command
        """

        (stdout, stderr) = SystemCommandsModule.execute_command('ls')
        assert_true(len(stderr) == 0)

    def test_2_execute_command_ssh(self) -> None:
        """
        Execute ls command
        """

        (stdout, stderr) = SystemCommandsModule.execute_command('ls', sudo=False, host=self.ssh_host,
                                                                port=self.ssh_port,
                                                                user=self.ssh_username, password=self.ssh_password)
        assert_true(len(stderr) == 0)

    def test_3_used_space_percent(self) -> None:
        """
        Execute used_space_percent command
        """

        used_space_percent = SystemCommandsModule.used_space_percent('/',
                                                                    host=self.ssh_host, port=self.ssh_port,
                                                                    user=self.ssh_username, password=self.ssh_password)
        assert_true(used_space_percent >= 0)

    def test_4_consumed_ram_percent(self) -> None:
        """
        Execute consumed_ram_percent command
        """

        consumed_ram_percent = SystemCommandsModule.consumed_ram_percent(host=self.ssh_host, port=self.ssh_port,
                                                                         user=self.ssh_username, password=self.ssh_password)
        assert_true(consumed_ram_percent >= 0)

    def test_5_load_cpu(self) -> None:
        """
        Execute load_cpu command
        """

        load = SystemCommandsModule.load_cpu(host=self.ssh_host, port=self.ssh_port,
                                             user=self.ssh_username, password=self.ssh_password)
        assert_true(load >= 0)

    def test_6_get_process_dict(self) -> None:
        """
        Execute get_process_dict command
        """

        process_dict = SystemCommandsModule.get_process_dict(host=self.ssh_host, port=self.ssh_port,
                                                     user=self.ssh_username, password=self.ssh_password)
        assert_true(len(process_dict) > 0)

    def test_7_is_process_name_active(self) -> None:
        """
        Execute is_process_name_active command
        """

        process_name = 'systemd'
        result = SystemCommandsModule.is_process_name_active(process_name, host=self.ssh_host, port=self.ssh_port,
                                                             user=self.ssh_username, password=self.ssh_password)
        assert_true(result)

    def test_8_is_process_pid_active(self) -> None:
        """
        Execute is_process_pid_active command
        """

        pid = 1
        result = SystemCommandsModule.is_process_pid_active(pid, host=self.ssh_host, port=self.ssh_port,
                                                            user=self.ssh_username, password=self.ssh_password)
        assert_true(result)

    def test_9_execute_command(self) -> None:
        """
        Execute sh script command
        """

        (stdout, stderr) = SystemCommandsModule.execute_command('/bin/bash test/test.sh')
        assert_true(len(stderr) == 0)

    def test_10_execute_command(self) -> None:
        """
        Execute sh script command in thread
        """

        SystemCommandsModule.execute_command('/bin/bash test/test.sh', execute_in_thread=True)
        assert_true(True)