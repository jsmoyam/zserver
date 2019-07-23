from common.app_model import AppHTTPStatus, ErrorCode
from common.infra_modules.infra_exception import InfraException


# region ErrorCodes

class DatabaseErrorCode(ErrorCode):
    """
    Database module error codes. Codes from 20 to 29.
    """

    DATABASE_ERROR = \
        20, 'ERROR', 'Error: {}', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_CONNECTION_ERROR = \
        21, 'CONNECTION_ERROR', 'Could not connect to database', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_CREATE_ERROR = 22, 'CREATE_ERROR', 'Error creating data', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_READ_ERROR = 23, 'READ_ERROR', 'Error reading data', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_UPDATE_ERROR = 24, 'UPDATE_ERROR', 'Error updating data', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_DELETE_ERROR = 25, 'DELETE_ERROR', 'Error deleting data', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_EXEC_QUERY_ERROR = 26, 'EXEC_QUERY_ERROR', 'Error executing query', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_CONFIGURATION_CONVERTER_ERROR = \
        27, 'CONFIGURATION_CONVERTER_ERROR', 'Error configuring converter methods', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_CONFIGURATION_ERROR = \
        28, 'CONFIGURATION_ERROR', 'Error configuring module', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATABASE_CONF_KEY_ERROR = \
        29, 'CONF_KEY_ERROR', '{} key was not found', AppHTTPStatus.INTERNAL_SERVER_ERROR

# endregion


# region Exceptions

class DatabaseException(InfraException):
    pass

# endregion
