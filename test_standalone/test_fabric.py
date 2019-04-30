import re
import fabric

def execute_command(command, sudo, host, user, port):
    regexp = '^localhost$|^127(?:\.[0-9]+){0,2}\.[0-9]+$|^(?:0*\:)*?:?0*1$'
    is_localhost = bool(re.search(regexp, host))

    # Create fabric connection
    output = (None, None)
    if is_localhost:
        conn = fabric.Connection(host)
        modified_command = 'sudo ' + command if sudo else command
        output = conn.local(modified_command)
    else:
        conn = fabric.Connection(host, user=user, port=port)
        output = conn.sudo(command) if sudo else conn.run(command)

    return (output.stdout, output.stderr)

# output = execute_command('ls', False, 'localhost', None, None)
# print(output.stdout)
print('------------------------------------------------')
# execute_command('cat /etc/shadow', True, 'localhost', None, None)
# print('------------------------------------------------')
# output = execute_command('cat /etc/shadow', True, 'raspberry', 'pi', 22)
# print(output.stdout)
print('------------------------------------------------')
# execute_command('cat /etc/passwd', False, 'raspberry', 'pi', 22)

stdout, stderr = execute_command('hciconfig hci0 piscan', True, 'localhost', '', 22)
# stdout, stderr = execute_command('hciconfig hci0 piscan', True, 'raspberry', 'pi', 22)
print(stdout)
print('.....................')
print(stderr)