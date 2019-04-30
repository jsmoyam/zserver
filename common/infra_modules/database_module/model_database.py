from common.app_model import DataResult
from common.infra_modules.infra_exception import InfraException


class DatabaseResult:
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


class DatabaseException(InfraException):
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
