from marshmallow import Schema, fields

from common.app_model import DataResult


class LoginInputData:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class LoginInputDataSchema(Schema):
    username = fields.Str()
    password = fields.Str()


class AAAResult(DataResult):

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        DataResult.__init__(self, code, data, msg, exception)
