import ast
from marshmallow import Schema, fields

from common.app_model import DataResult
from common.infra_modules.infra_exception import InfraException


class VirtMachineData:
    """
    Class of standard data input
    """

    def __init__(self):
        self.ram_usage = None
        self.disk_commited = None
        self.name = None
        self.ram_assigned = None
        self.cpu_usage = None
        self.disks = list()

    def __repr__(self):
        return '{}'.format(self.name)


class VirtMachineDataSchema(Schema):
    ram_usage = fields.Int()
    disk_commited = fields.Int()
    name = fields.Str()
    ram_assigned = fields.Int()
    cpu_usage = fields.Int()
    disks = fields.List(fields.Dict())

class VirtMachineListData:

    def __init__(self, vm_list):
        self.vm_list = vm_list

    def __repr__(self):
        return "test"


class VirtMachineListDataSchema(Schema):
    vm_list = fields.List(fields.Nested(VirtMachineDataSchema))

class VirtInfraData:
    """
    Class of standard data input
    """
    def __init__(self):
        self.memory_total = None
        self.memory_used = None
        self.cpu_total = None
        self.cpu_used = None
        self.disk_total = None
        self.disk_used = None

    def __repr__(self):
        return '{} {} {} {} {} {}'.format(self.memory_total, self.memory_used, self.cpu_total, self.cpu_used, self.disk_total, self.disk_used)


class VirtInfraDataSchema(Schema):

    memory_total = fields.Int()
    memory_used = fields.Int()
    cpu_total = fields.Int()
    cpu_used = fields.Int()
    disk_total = fields.Int()
    disk_used = fields.Int()




class VirtResult:
    """
    Class of standard data result
    """

    # Module codes
    CODE_OK = 'OK'
    CODE_KO = 'KO'

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        DataResult.__init__(self, code, data, msg, exception)

    def __repr__(self):
        return str(self.__dict__)


class VirtException(InfraException):
    pass


class ErrorMessages:
    """
    Class of standar messages of the module
    """

    # Error messages
    CONNECTION_ERROR = 'Could not connect to datastore'
    GET_ERROR = 'Error getting data'
    PUT_ERROR = 'Error storing data'
    CONFIGURATION_ERROR = 'Error configuring datastore'
    ID_ERROR = 'Error in the ID format'
    SCHEMA_ERROR = 'Error accessing non-existent schema'
