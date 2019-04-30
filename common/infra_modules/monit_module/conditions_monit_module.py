import builtins
import sqlalchemy
import requests

from common import config
from common.infra_modules.monit_module import MODULE_NAME
from common.infra_modules.system_commands_module.system_commands_module import SystemCommandsModule

logger = config.get_log(MODULE_NAME)


def execute_shell(arg_list, additional_data):
    """
    Execute shell command
    :param arg_list: arg_list[0] is the command, arg_list[1] is sudo mode, arg_list[2] is the type to convert
    :param additional_data: data for ssh connection
    :return: tuple str with (stdout, stderr)
    """

    if len(arg_list) == 2:
        type_to_convert = getattr(builtins, 'str')
    else:
        type_to_convert = getattr(builtins, arg_list[2])

    command = arg_list[0]
    sudo = True if arg_list[1].lower() == 'true' else False
    host = additional_data.host
    port = additional_data.port
    username = additional_data.username
    password = additional_data.password

    out, err = SystemCommandsModule.execute_command(command, sudo=sudo, host=host, port=port, user=username,
                                                    password=password)
    return type_to_convert(out)


def db_query(arg_list, additional_data) -> str:
    """
    Execute a sql query in database (only select)
    :param arg_list: [database connection, query]
    :param additional_data: None
    :return: str with comma separator or throw exception if query fails
    """

    engine = sqlalchemy.create_engine(arg_list[0])
    with engine.connect() as con:
        rs = con.execute(arg_list[1])

        output = ''
        for row in rs:
            output = output + ',' + row[0]

        return output[1:]


def db_exec(arg_list, additional_data) -> str:
    """
    Execute a sql command in database
    :param arg_list: [database connection, command, (optional default 1) position of the item to return as string]
    :param additional_data: None
    :return: str as tuple with comma separator or throw exception if query fails
    """

    if len(arg_list) == 2:
        target_row = 1
    else:
        target_row = arg_list[2]

    engine = sqlalchemy.create_engine(arg_list[0])
    with engine.connect() as con:
        rs = con.execute(arg_list[1])

        number_row = 1
        for row in rs:
            if number_row == target_row:
                return ','.join(map(str, row))
            else:
                number_row = number_row + 1


def http_get(arg_list, additional_data) -> str:
    """
    Send http get request to a server
    :param arg_list: arg_list[0] is the url
    :param additional_data: None
    :return: output of server
    """
    url = arg_list[0]
    r = requests.get(url=url)
    return r.text


def http_get_with_condition_result(arg_list, additional_data) -> str:
    """
    Send http get request to a server
    :param arg_list: arg_list[0] is the url
    :param additional_data: condition result is in variable condition_result
    :return: output of server
    """
    url = arg_list[0]
    data = {'data': additional_data.condition_result}
    r = requests.get(url=url, params=data)
    return r.text
    # contents = urllib.request.urlopen(url).read()
    # return contents.decode('utf-8')


def used_space_percent(arg_list, additional_data) -> int:
    """
    Return used space in percent of a mount point
    :param arg_list: arg_list[0] is mount point
    :param additional_data: data for ssh connection
    :return: used space in percent
    """

    mount_point = arg_list[0]
    host = additional_data.host
    port = additional_data.port
    username = additional_data.username
    password = additional_data.password
    output = SystemCommandsModule.used_space_percent(mount_point, host=host, port=port,
                                                     user=username, password=password)
    return output


def check_used_space_percent(arg_list, additional_data) -> str:
    """
    Return first mount point in which used space is greather than value
    :param arg_list: arg_list[0] is mount point, arg_list[1] is the value
    :param additional_data: data for ssh connection
    :return: mount point
    """

    mount_point = arg_list[0]
    value = arg_list[1]
    host = additional_data.host
    port = additional_data.port
    username = additional_data.username
    password = additional_data.password
    output = SystemCommandsModule.check_used_space_percent(mount_point, value, host=host, port=port,
                                                           user=username, password=password)
    return output


def consumed_ram(arg_list, additional_data) -> int:
    """
    Return used ram percentage
    :param arg_list: None
    :param additional_data: data for ssh connection
    :return: used space in percent
    """

    host = additional_data.host
    port = additional_data.port
    username = additional_data.username
    password = additional_data.password
    output = SystemCommandsModule.consumed_ram_percent(host=host, port=port, user=username, password=password)
    return output


def load_cpu(arg_list, additional_data) -> int:
    """
    Return load cpu as int (from 0 to 100)
    :param arg_list: None
    :param additional_data: data for ssh connection
    :return: cpu load in range 0-100
    """

    host = additional_data.host
    port = additional_data.port
    username = additional_data.username
    password = additional_data.password
    output = SystemCommandsModule.load_cpu(host=host, port=port, user=username, password=password)
    return output