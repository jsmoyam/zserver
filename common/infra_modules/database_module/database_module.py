from common import config
from common.infra_modules.infra_module import InfraModule
from common.infra_tools.decorators import log_function
from common.infra_modules.database_module import MODULE_NAME
from common.infra_modules.database_module.model_database import DatabaseException
from common.infra_modules.database_module.impl.database_api import DatabaseApi
from common.infra_modules.database_module.impl.database_api_factory import DatabaseApiFactory


logger = config.get_log(MODULE_NAME)


class DatabaseModule(InfraModule):
    """
    Main class of module
    """

    def initialize(self):
        """
        Get configuration and connection object
        """

        self.orm_type = self.module_config.get_value(MODULE_NAME, 'orm_type')
        self.connection_database = self.module_config.get_value(MODULE_NAME, 'connection_database')
        self.db = DatabaseApiFactory.get_connection(self.orm_type, self.connection_database)

    def exit(self) -> None:
        logger.info('SHUTDOWN MODULE')

    #@log_function(logger)
    def exec_query(self, query: str) -> list:
        """
        Execute query
        :param query: query to exec
        :return: list with data
        """

        try:
            ret = self.db.exec_query(query)
            return ret
        except DatabaseException as e:
            logger.error('Error executing query', exc_info=True)
            return None

    @log_function(logger)
    def insert(self, table: str, data: dict) -> bool:
        """
        Insert row in table
        :param table: table to insert
        :param data: data to insert
        :return: operation status
        """

        try:
            ret = self.db.insert(table, data)
            return ret
        except DatabaseException as e:
            logger.error('Error inserting data', exc_info=True)
            return None

    @log_function(logger)
    def read(self, table: str, sql_filter: str) -> list:
        """
        Read rows in table with filter
        :param table: table to read
        :param sql_filter: filter to select
        :return: row list
        """

        try:
            ret = self.db.read(table, sql_filter)
            return ret
        except DatabaseException as e:
            logger.error('Error reading data', exc_info=True)
            return None

    @log_function(logger)
    def update(self, table: str, data: dict, sql_filter: str) -> bool:
        """
        Update rows in table
        :param table: table to update
        :param data: data to update
        :param sql_filter: filter to search
        :return: operation status
        """

        try:
            ret = self.db.update(table, data, sql_filter)
            return ret
        except DatabaseException as e:
            logger.error('Error updating data', exc_info=True)
            return None

    @log_function(logger)
    def delete(self, table: str, sql_filter: str) -> bool:
        """
        Delete rows in table
        :param table: table to delete
        :param sql_filter: filter to search
        :return: operation status
        """

        try:
            ret = self.db.delete(table, sql_filter)
            return ret
        except DatabaseException as e:
            logger.error('Error inserting data', exc_info=True)
            return None
