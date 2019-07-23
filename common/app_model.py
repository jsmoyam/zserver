import logging
import uuid

from enum import IntEnum
from marshmallow import Schema, fields, post_dump


# region Models


class AppHTTPStatus(IntEnum):
    """
    HTTP status codes and reason phrases
    """

    def __new__(cls, value, phrase, description=''):
        """
        Create a new enum

        :param value:  value of the http status
        :param phrase: short description
        :param description: description
        """

        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    OK = 200, 'OK', 'Request fulfilled, document follows'
    BAD_REQUEST = 400, 'Bad Request', 'Bad request syntax or unsupported method'
    UNAUTHORIZED = 401, 'Unauthorized', 'No permission -- see authorization schemes'
    FORBIDDEN = 403, 'Forbidden', 'Request forbidden -- authorization will not help'
    NOT_FOUND = 404, 'Not Found', 'Nothing matches the given URI'
    METHOD_NOT_ALLOWED = 405, 'Method Not Allowed', 'Specified method is invalid for this resource'
    UNPROCESSABLE_ENTITY = 422, 'Unprocessable Entity'
    TOO_MANY_REQUESTS = 429, 'Too Many Requests', 'The user has sent too many requests'
    INTERNAL_SERVER_ERROR = 500, 'Internal Server Error', 'Server got itself in trouble'
    BAD_GATEWAY = 502, 'Bad Gateway', 'Invalid responses from another server/proxy'
    SERVICE_UNAVAILABLE = 503, 'Service Unavailable', 'The server cannot process the request due to a high load'


class AppDataResult:
    """
    Standard data result from the API
    """

    def __init__(self, status_code: AppHTTPStatus, success: bool, data: dict = None, msg: str = '',
                 error: Exception = None):
        """
        Constructor: Instance the AppDataResult

        :param status_code: http status code
        :param success: true or false
        :param data: data output
        :param msg: message output
        :param error: exception if exists
        """

        self.status_code = status_code
        self.success = success
        self.data = data
        self.msg = msg
        self.error = error

    def __repr__(self) -> str:
        """
        Return a printable representation of the object

        :return: string with the object
        :rtype: str
        """

        return str(self.__dict__)


class ErrorCode(IntEnum):
    """
    Standard error exception of the app
    """

    def __new__(cls, value, phrase, message: str, code_http: AppHTTPStatus):
        """
        Create a new enum

        :param value: value of the error
        :param phrase: Error short description
        :param message: Error description
        """

        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.message = message
        obj.code_http = code_http
        obj.trace_id = uuid.uuid4()
        return obj

    def __str__(self):
        """
        Print the object

        :return: string with the object values
        :rtype: str
        """

        return "{}. Trace-ID: {}".format(self.message, self.trace_id)

    def formatter(self, format_spec):
        """
        Print the object formatted with text

        :param format_spec: text to input

        :return: string formatted
        :rtype: str
        """

        self.message = self.message.format(format_spec)

        return self


class AppMessage:
    pass


# endregion


# region Schemas


class _AppDataResultBaseSchema(Schema):
    """
    Base schema to generate AppDataResult
    """

    # Control values to skip.
    # Skip none and empty values
    SKIP_VALUES = (None, '')

    @post_dump
    def remove_skip_values(self, data):
        """
        Remove all keys with empty or none values

        :param data: data input to check

        :return: resulting schema
        :rtype: dict
        """

        return {
            key: value for key, value in data.items()
            if value not in self.SKIP_VALUES
        }


class AppErrorCodesSchema(Schema):
    """
    Standard schema to AppErrorCodes
    """

    code = fields.Integer(attribute="value")
    phrase = fields.Str()
    message = fields.Str()
    trace_id = fields.Str()


class AppDataResultSchema(_AppDataResultBaseSchema):
    """
    Standard schema to AppDataResult
    """

    status_code = fields.Integer()
    data = fields.Dict()
    success = fields.Boolean()
    msg = fields.Str()
    error = fields.Nested(AppErrorCodesSchema)


# endregion


# region Exceptions


class AppException(Exception):
    """
    Standard exception of the app
    """

    def __init__(self, error_code: ErrorCode = None, logger=None, level: int = logging.WARNING):
        """
        Constructor

        :param error_code: AppErrorCode
        :param logger: logger to print exception
        :param level: exception's level
        """

        self.error_code = error_code

        if logger:
            logger.log(level, error_code.message)
        Exception.__init__(self, error_code.message)


# endregion


# region ErrorCodes


class AppErrorCode(ErrorCode):
    """
    App error codes. Codes from 0 to 19
    """

    APP_UNKNOWN_ERROR = 0, 'Internal Server Error', 'Something is broken', AppHTTPStatus.INTERNAL_SERVER_ERROR
    APP_UNAUTHORIZED_ERROR = \
        1, 'Unauthorized', 'Missing or incorrect authentication credentials', AppHTTPStatus.UNAUTHORIZED
    APP_BAD_REQUEST_ERROR = \
        2, 'Bad Request', 'The request was invalid', AppHTTPStatus.BAD_REQUEST
    APP_FORBIDDEN_ERROR = \
        3, 'Forbidden', 'The request is understood, but it has been refused or access is not allowed', \
        AppHTTPStatus.FORBIDDEN
    APP_NOT_FOUND_ERROR = \
        4, 'Not Found', 'The URI requested is invalid or the resource requested', AppHTTPStatus.NOT_FOUND
    APP_METHOD_NOT_ALLOWED = \
        5, 'Method Not Allowed', 'Specified method is invalid for this resource', AppHTTPStatus.METHOD_NOT_ALLOWED
    APP_UNPROCESSABLE_ERROR = \
        6, 'Unprocessable Entity', 'The data is unable to be processed', \
        AppHTTPStatus.UNPROCESSABLE_ENTITY
    APP_TOO_MANY_REQUESTS_ERROR = \
        7, 'Too Many Requests', \
        'Request cannot be served due to the app\'s rate limit having been exhausted for the resource', \
        AppHTTPStatus.TOO_MANY_REQUESTS
    APP_BAD_GATEWAY_ERROR = \
        8, 'Bad Gateway', 'App is down, or being upgraded', \
        AppHTTPStatus.BAD_GATEWAY
    APP_SERVICE_UNAVAILABLE_ERROR = \
        9, 'Service Unavailable', 'The server are up, but overloaded with requests. Try again later', \
        AppHTTPStatus.SERVICE_UNAVAILABLE
    APP_CONF_API_ERROR = 9, 'Bad configuration API', 'Error in API configuration', AppHTTPStatus.INTERNAL_SERVER_ERROR
    APP_CONF_SSL_ERROR = \
        10, 'SSL configuration error', 'Error in SSL configuration', AppHTTPStatus.INTERNAL_SERVER_ERROR
    APP_SSL_ERROR = 11, 'SSL Certified or key error', 'Error in SSL', AppHTTPStatus.INTERNAL_SERVER_ERROR
    APP_CONF_KEYFILE_ERROR = \
        12, 'Server configuration error', '{} key was not found', AppHTTPStatus.INTERNAL_SERVER_ERROR
    APP_CONF_MODULE_EXP = \
        13, 'Server configuration error', 'Error in the configuration of the module exposed {}', \
        AppHTTPStatus.INTERNAL_SERVER_ERROR
    APP_LOG_NOT_FOUND = 14, 'Logger configuration error', '{} logger was not found', AppHTTPStatus.NOT_FOUND
    APP_MODULE_NOT_FOUND = 15, 'Server configuration error', '{} module was not found', AppHTTPStatus.NOT_FOUND
    APP_STOP_API_ERROR = \
        16, 'Stop API error', 'Not running with the Werkzeug Server', AppHTTPStatus.INTERNAL_SERVER_ERROR
    EXECUTED_COMMAND_ERROR = \
        17, 'Bad command', 'Error executing command', AppHTTPStatus.INTERNAL_SERVER_ERROR

# endregion
