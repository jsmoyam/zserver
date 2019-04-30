from marshmallow import Schema, fields

from common.app_model import DataResult
from sky_modules.sky_module import SkyException


test1_get_args = { 'id': fields.Int() }


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


class TestResult(DataResult):

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        DataResult.__init__(self, code, data, msg, exception)


class HuntingException(SkyException):
    pass
