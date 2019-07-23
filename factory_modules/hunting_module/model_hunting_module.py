from marshmallow import Schema, fields

from common.app_model import AppDataResult
from factory_modules.factory_module import FactoryException

import time

test1_get_args = { 'id': fields.Int() }


class HuntingHostData:
    def __init__(self, ip, hostname, channel_name):
        self.ip = ip
        self.hostname = hostname
        self.date_creation = self.date_modified = time.time()
        self.agent_available = 0
        self.forest_available = 0
        self.channel_name = channel_name
        self.country = 1

class HuntingHostDataSchema(Schema):

    ip = fields.Str()
    hostname = fields.Str()
    date_creation = fields.Int()
    date_modified = fields.Int()
    agent_available = fields.Int()
    forest_available = fields.Int()
    channel_name = fields.Int()
    country = fields.Str()


class HuntingChannelData:
    def __init__(self, name, hunting_type, gevo_associated, concurrence_type, concurrence_time, scheduling):
        self.name = name
        self.hunting_type = hunting_type
        self.gevo_associated = gevo_associated
        self.concurrence_type = concurrence_type
        self.concurrence_time = concurrence_time
        self.scheduling = scheduling

class HuntingChannelDataSchema(Schema):
    name = fields.Str()
    hunting_type = fields.Str()
    gevo_associated = fields.Str()
    concurrence_type = fields.Str()
    concurrence_time = fields.Str()
    scheduling = fields.Str()

class HuntingResult(AppDataResult):

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        AppDataResult.__init__(self, code, data, msg, exception)




class Test1InputData:
    def __init__(self, data1: int, data2: int):
        self.data1 = data1
        self.data2 = data2


class Test1InputDataSchema(Schema):
    data1 = fields.Int()
    data2 = fields.Int()


class TestData:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __repr__(self):
        # This method always return string
        return '{} {} {} {}'.format(self.a, self.b, self.c, self.d)


class Test2Data:
    def __init__(self, f):
        self.f = f


class Test2Schema(Schema):
    f = fields.List(fields.Bool())

class TestSchema(Schema):
    a = fields.Int()
    b = fields.Int()
    c = fields.Nested(Test2Schema)
    d = fields.List(fields.Str())
    e = fields.List(fields.Nested(Test2Schema))


class TestResult(AppDataResult):

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        AppDataResult.__init__(self, code, data, msg, exception)


class HuntingException(FactoryException):
    pass


class ErrorMessages:
    """
    Class of standar messages of the module
    """

    # Error messages
    CONNECTION_ERROR = 'Could not connect to database'
    CREATE_ERROR = 'Error creating data'
    READ_ERROR = 'Error reading data'
    UPDATE_ERROR = 'Error updating data'
    DELETE_ERROR = 'Error deleting data'
    CONFIGURATION_ERROR = 'Error configuring module'
    SCHEMA_ERROR = 'Error accessing non-existent schema'