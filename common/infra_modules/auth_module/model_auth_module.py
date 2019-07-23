from marshmallow import Schema, fields

from common.app_model import AppHTTPStatus, AppDataResult, ErrorCode, AppMessage
from common.infra_modules.infra_exception import InfraException


# region Models


class AuthResult(AppDataResult):
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


class LoginInputData:
    """
    Class that defines the login input data from api request
    """

    def __init__(self, username: str, password: str):
        """
        Constructor: Init variables from request

        :param username: user's username
        :param password: user's password
        """

        self.username = username
        self.password = password


class LogoutInputData:
    """
    Class that defines the logout input data from api request
    """

    def __init__(self, token: str):
        """
        Constructor: Init variables from request

        :param token: user's token
        """

        self.token = token


# endregion


# region Schemas


class LoginInputDataSchema(Schema):
    """
    Schema to LoginInputData
    """
    username = fields.Str()
    password = fields.Str()


class LogoutInputDataSchema(Schema):
    """
    Schema to LogoutInputData
    """
    token = fields.Str()


# endregion


# region Messages


class AuthMessage(AppMessage):
    """
    Auth module messages
    """
    AUTH_USER_LOGIN = 'User login successfully'
    AUTH_USER_LOGOUT = 'User logout successfully'


# endregion


# region ErrorCodes


class AuthErrorCode(ErrorCode):
    """
    Auth module error codes. Codes from 30 to 39.
    """

    AUTH_USER_NOT_FOUND = 30, 'USER_NOT_FOUND', 'User {} not found', AppHTTPStatus.NOT_FOUND
    AUTH_TOKEN_EXPIRED = 31, 'TOKEN_EXPIRED', 'Token expired', AppHTTPStatus.BAD_REQUEST
    AUTH_TOKEN_BAD_SIGNATURE = 32, 'TOKEN_BAD_SIGNATURE', 'Token bad signature', AppHTTPStatus.BAD_REQUEST
    AUTH_TOKEN_DOES_NOT_EXIST = 33, 'TOKEN_DOES_NOT_EXIST', 'Token does not exist', AppHTTPStatus.BAD_REQUEST
    AUTH_USER_PERMISSIONS_NOT_FOUND = \
        34, 'USER_PERMISSIONS_NOT_FOUND', 'Permissions not found for user {}', AppHTTPStatus.NOT_FOUND
    AUTH_USER_DOES_NOT_PERMISSION = \
        35, 'USER_DOES_NOT_PERMISSION', 'Forbidden. Access is not allowed', AppHTTPStatus.FORBIDDEN


# endregion


# region Exceptions

class AuthException(InfraException):
    pass

# endregion
