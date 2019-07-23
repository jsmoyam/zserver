from common.app_model import AppHTTPStatus, AppDataResult, ErrorCode
from factory_modules.factory_module import FactoryException


# region Models

class DatasourceResult(AppDataResult):
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


# endregion


# region ErrorCodes

class DatasourceErrorCode(ErrorCode):
    """
    Datasource module error codes. Codes from 40 to 49.
    """

    DATASOURCE_DB_ERROR = 40, 'DATABASE_ERROR', 'Error with database', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATASOURCE_DB_ERROR_DES = 41, 'DATABASE_ERROR', 'Error with database: {}', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATASOURCE_ENTITY_NOT_FOUND = 42, 'NOT_FOUND', '{} not found', AppHTTPStatus.NOT_FOUND
    DATASOURCE_ENTITY_DELETE_ERROR = 43, 'DELETE_ERROR', 'Error deleting {}', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATASOURCE_ENTITY_UPDATE_ERROR = 44, 'UPDATE_ERROR', 'Error updating {}', AppHTTPStatus.INTERNAL_SERVER_ERROR
    DATASOURCE_ENTITY_CREATE_ERROR = 45, 'CREATE_ERROR', 'Error creating {}', AppHTTPStatus.INTERNAL_SERVER_ERROR

# endregion


# region Exceptions

class DatasourceException(FactoryException):
    pass

# endregion
