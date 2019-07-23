import os
import configparser
import importlib

from common import config
from common.app_model import AppException
from common.infra_modules.infra_module import InfraModule
from common.infra_modules.database_module import MODULE_NAME
from common.infra_modules.database_module.model_database_module import DatabaseException, DatabaseErrorCode
from common.infra_modules.database_module.impl.database_factory import DatabaseFactory
from common.infra_tools.decorators import log_function

# Get the module logger
logger = config.get_log(MODULE_NAME)


class DatabaseModule(InfraModule):
    """
    Main class of module
    """

    # Get the database configuration file
    CONVERTER_FILE = 'converter'
    CONVERTER_FILE_EXTENSION = '.properties'
    CONVERTER_FILE_FOLDER = 'etc'

    CONVERTER_PATH = os.path.dirname(__file__) + os.sep + CONVERTER_FILE_FOLDER + os.sep
    CONVERTER_FILE_FULL_PATH = CONVERTER_PATH + CONVERTER_FILE + CONVERTER_FILE_EXTENSION

    # Base file to call converter methods
    CONVERTER_SECTION = 'converter_section'

    orm_type: object
    connection_database: object
    isolation_level: str
    db: object
    db_config = dict()

    def initialize(self):
        """
        Get configuration and connection object
        """

        self.orm_type = self.module_config.get_value(MODULE_NAME, 'orm_type')
        self.connection_database = self.module_config.get_value(MODULE_NAME, 'connection_database')
        self.isolation_level = self.module_config.get_value(MODULE_NAME, 'isolation_level')
        self.db = DatabaseFactory.get_connection(self.orm_type, self.connection_database, self.isolation_level)

        # Load the configuration
        config_file = self.CONVERTER_FILE_FULL_PATH

        try:
            with open(config_file, 'r') as f:
                config_string = '[' + self.CONVERTER_SECTION + ']\n' + f.read()
            config_parser = configparser.ConfigParser()
            config_parser.read_string(config_string)
            self.db_config = config_parser
        except FileNotFoundError:
            raise DatabaseException(DatabaseErrorCode.DATABASE_CONFIGURATION_ERROR)

    @log_function(logger)
    def exec_query(self, query: str) -> list:
        """
        Execute query passed by parameter

        :param query: query to exec

        :return: list with data
        :rtype: list
        """

        try:
            ret = self.db.exec_query(query)
            return ret
        except DatabaseException:
            logger.error(DatabaseErrorCode.DATABASE_EXEC_QUERY_ERROR)
            return None

    @log_function(logger)
    def insert(self, table: str, data: dict) -> bool:
        """
        Insert row in table

        :param table: table to insert
        :param data: data to insert

        :return: operation status
        :rtype: bool
        """

        try:
            ret = self.db.insert(table, data)
            return ret
        except DatabaseException:
            logger.error(DatabaseErrorCode.DATABASE_CREATE_ERROR)
            return None

    @log_function(logger)
    def insert_from_obj(self, obj: object) -> bool:
        """
        Insert object in table

        :param obj: object to insert

        :return: operation status
        :rtype: bool
        """

        try:
            # Get the converter method
            converter_method = self.__get_converter_method__(obj)

            # Get the data converted
            object = converter_method(self, obj)

            return self.db.insert(object)

        except Exception as e:
            if isinstance(e, AppException):
                logger.error(e.error_code)
                raise DatabaseException(e.error_code)
            else:
                output_error = DatabaseErrorCode.DATABASE_CREATE_ERROR
                logger.error(output_error)
                raise DatabaseException(output_error)

    @log_function(logger)
    def read(self, table: str, sql_filter: str = '') -> list:
        """
        Read rows in table with optional filter

        :param table: table to read
        :param sql_filter: filter to select

        :return: row list
        :rtype: list
        """

        try:
            ret = self.db.read(table, sql_filter)
            return ret
        except DatabaseException:
            logger.error(DatabaseErrorCode.DATABASE_READ_ERROR)
            return None

    @log_function(logger)
    def read_from_obj(self, obj: object = None) -> bool:
        """
        Read rows in table with optional filter

        :param obj: filter to select

        :return: row list
        :rtype: list
        """

        try:
            # Get the converter method
            converter_method = self.__get_converter_method__(obj)

            # Get the data converted
            args, kwargs = converter_method(self, obj)

            return self.db.read(*args, **kwargs)

        except Exception as e:
            if isinstance(e, AppException):
                logger.error(e.error_code)
                raise DatabaseException(e.error_code)
            else:
                output_error = DatabaseErrorCode.DATABASE_READ_ERROR
                logger.error(output_error)
                raise DatabaseException(output_error)

    @log_function(logger)
    def update(self, table: str, data: dict, sql_filter: str = '') -> bool:
        """
        Update rows in table with optional filter

        :param table: table to update
        :param data: data to update
        :param sql_filter: filter to search

        :return: operation status
        """

        try:
            ret = self.db.update(table, data, sql_filter)
            return ret
        except DatabaseException:
            logger.error(DatabaseErrorCode.DATABASE_UPDATE_ERROR)
            return None

    @log_function(logger)
    def update_from_obj(self, obj: object) -> bool:
        """
        Update object in table

        :param obj: object to update

        :return: operation status
        :rtype: bool
        """

        try:
            # Get the converter method
            converter_method = self.__get_converter_method__(obj)

            # Get the data converted
            updated_obj = converter_method(self, obj)

            return self.db.update(updated_obj)

        except Exception as e:
            if isinstance(e, AppException):
                logger.error(e.error_code)
                raise DatabaseException(e.error_code)
            else:
                output_error = DatabaseErrorCode.DATABASE_UPDATE_ERROR
                logger.error(output_error)
                raise DatabaseException(output_error)

    @log_function(logger)
    def delete(self, table: str, sql_filter: str) -> bool:
        """
        Delete rows in table

        :param table: table to delete
        :param sql_filter: filter to search

        :return: operation status
        :rtype: bool
        """

        try:
            ret = self.db.delete(table, sql_filter)
            return ret
        except DatabaseException:
            logger.error(DatabaseErrorCode.DATABASE_DELETE_ERROR)
            return None

    @log_function(logger)
    def delete_from_obj(self, obj: object) -> bool:
        """
        Delete object in table

        :param obj: object to delete

        :return: operation status
        :rtype: bool
        """

        try:
            # Get the converter method
            converter_method = self.__get_converter_method__(obj)

            # Get the data converted
            object = converter_method(self, obj)

            return self.db.delete(object)

        except Exception as e:
            if isinstance(e, AppException):
                logger.error(e.error_code)
                raise DatabaseException(e.error_code)
            else:
                output_error = DatabaseErrorCode.DATABASE_DELETE_ERROR
                logger.error(output_error)
                raise DatabaseException(output_error)

    def __get_converter_method__(self, obj: object):
        """
        Recover converter method and return it

        :param obj: converter method

        :return: A method
        :rtype: function
        """

        cls_obj = None

        try:

            logger.debug('Getting the converter method for obj {}'.format(obj.__class__))

            # Get the converter from the configuration
            cls_parent = obj.__class__.__bases__[0]
            cls_obj = '{}.{}'.format(cls_parent.__module__, cls_parent.__name__)
            converter_obj = self.db_config[self.CONVERTER_SECTION][cls_obj]

            module_name = converter_obj.rsplit('.', 1)[0]
            method_name = converter_obj.split('.')[-1]

            # Import class
            module = importlib.import_module(module_name)

            # Get the method
            converter_method = getattr(module, method_name)

            if not converter_method:
                logger.debug('No converted method found for obj {}'.format(obj.__class__))
                raise DatabaseException(DatabaseErrorCode.DATABASE_CONFIGURATION_CONVERTER_ERROR)

            return converter_method

        except Exception:
            raise DatabaseException(DatabaseErrorCode.DATABASE_CONF_KEY_ERROR.formatter(cls_obj))
