import time
from marshmallow import Schema, fields

from common.app_model import AppDataResult


class AcquireInputData:
    def __init__(self, device: str, method: str, alias: str):
        self.device = device
        self.method = method
        self.alias = alias


class AcquireInputDataSchema(Schema):
    device = fields.Str()
    method = fields.Str()
    alias = fields.Str()


class AcquireData:
    def __init__(self, device: str, method: str, alias: str):
        self.device = device
        self.method = method
        self.alias = alias
        self.status = ""
        self.progress = 0
        self.id = str(time.time())
        self.hash_md5 = ""
        self.hash_sha256 = ""
        self.size = 0
        self.status = "idle"
        self.path = ""


class AcquireDataSchema(Schema):
    device = fields.Str()
    method = fields.Str()
    alias = fields.Str()
    status = fields.Str()
    progress = fields.Int()
    id = fields.Str()
    hash_md5 = fields.Str()
    hash_sha256 = fields.Str()
    size = fields.Int()
    path = fields.Str()


class AcquireDataList:
    def __init__(self, acquire_list):
        self.acquire_list = acquire_list


class AcquireDataListSchema(Schema):
    acquire_list = fields.List(fields.Nested(AcquireDataSchema))


class AcquireResult(AppDataResult):

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        AppDataResult.__init__(self, code, data, msg, exception)

