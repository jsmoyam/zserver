import Pyro4
import Pyro4.naming
import inspect

def get_commands_from_shell():
    """Recover all methods from shell module"""

    # First recover all methods from server
    obj = Pyro4.Proxy("PYRONAME:shell_manager_module")
    Pyro4.naming.type_meta(obj)
    all_methods = inspect.getmembers(obj)

    # Filter only by shell methods
    # methods[x][0] --> method name
    # methods[x][1] --> callable method
    shell_methods = [tup for tup in all_methods if tup[0].startswith('shell_')]

    # Rename method name removing SHELL_COMMAND_PREFIX
    methods = dict()
    for sm in shell_methods:
        method_name = sm[0][len('shell_'):]
        method_callable = sm[1]
        methods[method_name] = method_callable

    return methods

commands = get_commands_from_shell()
print(commands)

complete_command_as_list = [b'test1', b'5', b'6']
command = complete_command_as_list[0].decode("utf-8")
arguments = [x.decode("utf-8") for x in complete_command_as_list[1:]]

response = commands[command]((arguments,))

print('response {}'.format(response))

