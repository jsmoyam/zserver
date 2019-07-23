from marshmallow import Schema, fields

from typing import Dict, Union
from common.app_model import AppDataResult, AppHTTPStatus


class CpuStatData:
    def __init__(self):
        self.cpu_percent_usage = None

    def __repr__(self):
        return '{}'.format(self.cpu_percent_usage)


class RamStatData:
    def __init__(self):
        self.ram_total_memory = None
        self.ram_used_memory = None
        self.ram_free_memory = None
        self.ram_percent_usage_memory = None

    def __repr__(self):
        return '{} {} {} {}'.format(self.ram_total_memory, self.ram_used_memory,
                                    self.ram_free_memory, self.ram_percent_usage_memory)


class SwapStatData:
    def __init__(self):
        self.swap_total_memory = None
        self.swap_used_memory = None
        self.swap_free_memory = None
        self.swap_percent_usage_memory = None

    def __repr__(self):
        return '{} {} {} {}'.format(self.swap_total_memory, self.swap_used_memory,
                                    self.swap_free_memory, self.swap_percent_usage_memory)


class DiskStatData:
    def __init__(self):
        self.disk_device = None
        self.disk_mount_point = None
        self.disk_total_memory = None
        self.disk_used_memory = None
        self.disk_free_memory = None
        self.disk_percent_usage_memory = None

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.disk_device, self.disk_mount_point, self.disk_total_memory,
                                        self.disk_used_memory, self.disk_free_memory,
                                        self.disk_percent_usage_memory)


class SystemStatData:
    def __init__(self, cpu_stat: CpuStatData, ram_stat: RamStatData, swap_stat: SwapStatData, disk_stat: list):
        self.cpu_stat = cpu_stat
        self.ram_stat = ram_stat
        self.swap_stat = swap_stat
        self.disk_stat = disk_stat

    def __repr__(self):
        return '{} {} {} {}'.format(self.cpu_stat, self.ram_stat, self.swap_stat, self.disk_stat)


class RuleData:
    def __init__(self, name: str, condition: str, action_ok: str, action_ko: str):
        self.name = name
        self.condition = condition
        self.action_ok = action_ok
        self.action_ko = action_ko
        self.condition_evaluator = None
        self.action_ok_evaluator = None
        self.action_ko_evaluator = None

    def __repr__(self):
        return '{} {} {} {}'.format(self.name, self.condition, self.action_ok, self.action_ko)


class ServerData:
    def __init__(self, name: str, host: str, port: str, username: str, password: str, interval: int, rules: list):
        self.name = name
        self.host = host
        self.host_evaluator = None
        self.port = port
        self.username = username
        self.password = password
        self.interval = interval
        self.rules = rules

    def __repr__(self):
        return '{} {} {} {} {} {} {}'.format(self.name, self.host, self.port, self.username,
                                                'XXXX', self.interval, self.rules)

class AdditionalServerData:
    def __init__(self, name: str, host: str, port: str, username: str, password: str):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.condition_result = None

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.name, self.host, self.port, self.username, 'XXXX', self.condition_result)

class ShutdownData:
    def __init__(self, success: bool):
        self.success = success

    def __repr__(self):
        return '{}'.format(self.success)


class ShutdownSchema(Schema):
    success = fields.Bool()


class MonitResult(AppDataResult):
    """
    Class that defines the output data of the module views
    """

    def __init__(self, status_code: AppHTTPStatus, success: bool, data: dict = None, msg: str = '',
                 error: Exception = None):
        """
        Constructor: Init AppDataResult

        :param status_code: http status code
        :param success: true or false
        :param data: data to send
        :param msg: message for debug
        :param error: exception if exist
        """
        AppDataResult.__init__(self, status_code, success, data, msg, error)

class SystemStatisticsResultData:

    def __init__(self, system_statistics: Dict[str, Union[int, float]]) -> None:
        self.system_statistics = system_statistics
