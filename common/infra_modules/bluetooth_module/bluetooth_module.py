import time
import Pyro4
import Pyro4.naming
import inspect

from bluetooth import BluetoothSocket, advertise_service, RFCOMM, PORT_ANY, SERIAL_PORT_CLASS, SERIAL_PORT_PROFILE

import common
from common import config
from common.infra_modules.infra_module import InfraModule
from common.infra_modules.bluetooth_module import MODULE_NAME

from common.infra_tools.task_thread import TaskThread


# Instruction in Linux:
#
# sudo apt-get install python-dev libbluetooth-dev
# sudo apt-get install python-bluez
#
#
# This in turn requires the Bluetooth Daemon to run in compatibility mode.
#
# Start by editing the service startup parameters in its configuration file:
#
# sudo nano /etc/systemd/system/dbus-org.bluez.service
#
# Just add a -C after bluetoothd. The line should look like below:
#
# ExecStart=/usr/lib/bluetooth/bluetoothd -C
#
# Now reload the service configuration and restart the Bluetooth service with the following two commands
#
# sudo systemctl daemon-reload
# sudo systemctl restart dbus-org.bluez.service
#
# Finally, you can now load the Serial Port profile by issuing:
#
# sudo sdptool add SP
#
# You should get a Serial Port service registered message as a result, telling you that the operation was successful.


# This needs an entry in /etc/sudoers.d to execute with sudo with password the next command: hciconfig hci0 piscan:
# Cmnd_Alias VISIBLEBT = hciconfig hci0 piscan
# ALL ALL = NOPASSWD:VISIBLEBT


logger = config.get_log(MODULE_NAME)

# All module commands must start with this prefix
SHELL_COMMAND_PREFIX = 'shell_'

# Message to return if command not found
SYNTAX_COMMAND_ERROR = 'SYNTAX_COMMAND_ERROR'
SERVER_ERROR = 'SERVER_ERROR'


class BluetoothModule(InfraModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """

        self.service_name = self.module_config.get_value(MODULE_NAME, 'service_name')
        self.max_simultaneous_connections = int(self.module_config.get_value(MODULE_NAME, 'max_simultaneous_connections'))
        self.uuid = self.module_config.get_value(MODULE_NAME, 'uuid')
        self.wakeup_time = int(self.module_config.get_value(MODULE_NAME, 'wakeup_time'))
        self.scm = common.module_manager.get_module('system_commands_module')

        # Execute bluetooth server
        bluetooth_server = BluetoothServerTask(self.service_name, self.max_simultaneous_connections,
                                               self.uuid, self.wakeup_time, self.scm)
        bluetooth_server.set_only_one_execution()
        bluetooth_server.start()



class BluetoothServerTask(TaskThread):

    def __init__(self, service_name: str, max_simultaneous_connections: int, uuid: str, wakeup_time: int, scm: InfraModule):
        TaskThread.__init__(self)
        self.service_name = service_name
        self.max_simultaneous_connections = max_simultaneous_connections
        self.uuid = uuid
        self.wakeup_time = wakeup_time
        self.scm = scm

    def task(self):
        # Waiting until Bluetooth init is done
        time.sleep(self.wakeup_time)

        # Make device visible
        self.scm.set_bluetooth_visible()

        # Create a new server socket using RFCOMM protocol
        server_sock = BluetoothSocket(RFCOMM)

        # Bind to any port
        server_sock.bind(("", PORT_ANY))

        # Start listening
        server_sock.listen(self.max_simultaneous_connections)

        # Get the port the server socket is listening
        port = server_sock.getsockname()[1]

        # Main bluetooth server loop
        while True:

            logger.info('Waiting for bluetooth connection on channel {}'.format(port))

            client_sock = None
            try:
                # Block until we get a new connection
                client_sock, client_info = server_sock.accept()
                logger.info('Accepted connection from {}'.format(client_info))

                # Read the data sent by the client
                command = client_sock.recv(1024)
                if len(command) == 0:
                    continue

                logger.info('Received [{}]'.format(command))

                # Handle the request
                response = self.handle_request(command)

                client_sock.send(response)
                logger.info('Sent back [{}]'.format(response))

            except IOError:
                pass
            except KeyboardInterrupt:

                if client_sock is not None:
                    client_sock.close()

                server_sock.close()

                logger.info('Bluetooth server going down')
                break

    def handle_request(self, complete_command):
        # Parse complete command to get command and arguments (as list)
        complete_command_as_list = complete_command.split()
        command = complete_command_as_list[0].decode("utf-8")
        arguments = [x.decode("utf-8") for x in complete_command_as_list[1:]]

        # Add connection_mode
        arguments.extend(['bluetooth_mode'])

        # Execute command
        try:
            # Recover all methods from shell_manager_module
            commands = self.get_commands_from_shell()
            response = commands[command]((arguments,))
        except KeyError:
            response = SYNTAX_COMMAND_ERROR
        except Exception as e:
            logger.error('Server command error: {}'.format(e), exc_info=True)
            response = SERVER_ERROR

        return response

    def get_commands_from_shell(self):
        """Recover all methods from shell module"""

        # First recover all methods from server
        obj = Pyro4.Proxy("PYRONAME:shell_manager_module")
        Pyro4.naming.type_meta(obj)
        all_methods = inspect.getmembers(obj)

        # Filter only by shell methods
        # methods[x][0] --> method name
        # methods[x][1] --> callable method
        shell_methods = [tup for tup in all_methods if tup[0].startswith(SHELL_COMMAND_PREFIX)]

        # Rename method name removing SHELL_COMMAND_PREFIX
        methods = dict()
        for sm in shell_methods:
            method_name = sm[0][len(SHELL_COMMAND_PREFIX):]
            method_callable = sm[1]
            methods[method_name] = method_callable

        return methods
