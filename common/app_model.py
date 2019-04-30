import logging
from marshmallow import Schema, fields



class DataResult:
    """
    Class of standard data result
    """

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        self.code = code
        self.data = data
        self.msg = msg
        self.exception = exception

    def __repr__(self):
        return str(self.__dict__)


class DataResultSchema(Schema):
    code = fields.Str()
    data = fields.Dict()
    msg = fields.Str()


class AppException(Exception):
    """
    Standard exception
    """

    def __init__(self, msg: str = '', logger = None, level: int = logging.WARNING,) -> None:
        """
        Constructor with optional message

        :param msg: optional message of the exception
        :type msg: str

        :return: This function return nothing
        :rtype: None
        """
        if logger:
            logger.log(level, msg)
        Exception.__init__(self, msg)


class GenericErrorMessages:
    """
    Class of generic standard messages
    """

    # Error messages
    KEYFILE_ERROR = 'Not found the key'
    UNKNOWN_LOG_ERROR = 'Unknown log name'
    MODULE_NOT_FOUND = 'Module not found'
    CONFIGURATION_ERROR = 'Configuration error in config.ini'
    EXPOSED_CONFIGURATION_ERROR = 'Found exposed module without name. Please fill exposed_name property'
    VALIDATION_ERROR = 'Validation error'
    LOGIN_ERROR = 'API login error'
    WERKZEUG_NOT_RUNNING = 'Not running with the Werkzeug Server'
    EXPIRED_TOKEN_ERROR = 'Token expired'
    BAD_SIGNATURE_TOKEN_ERROR = 'Token bad signature'
    TOKEN_DOES_NOT_EXIST_ERROR = 'Token does not exist'
    USER_NOT_FOUND = 'User not found'
    USER_LOGIN = 'User login'
    TOKEN_LOGOUT_ERROR = 'Error trying logout token that not exist'
    DATABASE_ERROR = 'Error accessing database'
    EXECUTED_COMMAND_ERROR = 'Error executing command'