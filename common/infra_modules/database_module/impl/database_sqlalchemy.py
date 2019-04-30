import logging
import sqlalchemy

from common.infra_tools.decorators import log_function
from common.infra_modules.database_module import MODULE_NAME
from common.infra_modules.database_module.model_database import DatabaseException, ErrorMessages
from common.infra_modules.database_module.impl.database_api import DatabaseApi
from common.infra_modules.database_module.impl.database_generic import DatabaseGeneric


logger = logging.getLogger(MODULE_NAME)


class DatabaseSqlAlchemy(DatabaseApi, DatabaseGeneric):
    """
    Class to define the specific implementation of sql alchemy
    """

    def __init__(self, connection_database: str):
        """
        Constructor with connection string

        :param connection_database: url connection from ini file
        :return: This function return nothing
        """

        # Init the father class
        DatabaseApi.__init__(self, connection_database)

        try:
            # Connect with database
            conn, engine = self.open_connection()
            self.conn = conn
            self.engine = engine

        # TODO Catch exception for configuration error and raise exception
        # except errors.ConfigurationError:
        #     raise DatabaseException(ErrorMessages.CONFIGURATION_ERROR)
        except DatabaseException as e:
            raise e

    @log_function(logger, logging.DEBUG)
    def exec_query(self, query: str) -> list:
        """
        Execute query
        :param query: query to exec
        :return: list with dictionaries
        """
        list_of_rows = list()
        if query.lower().startswith('select'):
            rs = self.conn.execute(query)
            for row in rs:
                row_as_dict = dict(row)
                list_of_rows.append(row_as_dict)
        else:
            self.engine.execute(query)

        return list_of_rows

    @log_function(logger, logging.DEBUG)
    def insert(self, table: str, data: dict) -> bool:
        """
        Insert row in table
        :param table: table to insert
        :param data: data to insert
        :return: operation status
        """

        columns = ','.join(['"{}"'.format(x) for x in data.keys()])
        values = ','.join(['"{}"'.format(x) for x in data.values()])

        t = sqlalchemy.text('INSERT INTO {} ({}) VALUES ({})'.format(table, columns, values))
        t.execution_options(autocommit=True)
        self.conn.execute(t)
        return True

    @log_function(logger, logging.DEBUG)
    def read(self, table: str, sql_filter: str) -> list:
        """
        Read rows in table with filter
        :param table: table to read
        :param sql_filter: filter to select
        :return: row list
        """
        t = sqlalchemy.text('SELECT * FROM {} WHERE {}'.format(table, sql_filter))
        rs = self.conn.execute(t)
        list_of_rows = list()
        for row in rs:
            row_as_dict = dict(row)
            list_of_rows.append(row_as_dict)

        return list_of_rows

    @log_function(logger, logging.DEBUG)
    def update(self, table: str, data: dict, sql_filter: str) -> bool:
        """
        Update rows in table
        :param table: table to update
        :param data: data to update
        :param sql_filter: filter to search
        :return: operation status
        """

        values = ','.join(['{}="{}"'.format(k, v) for k, v in data.items()])

        t = sqlalchemy.text('UPDATE {} SET {} WHERE {}'.format(table, values, sql_filter))
        t.execution_options(autocommit=True)
        self.conn.execute(t)
        return True

    @log_function(logger, logging.DEBUG)
    def delete(self, table: str, sql_filter: str) -> bool:
        """
        Delete rows in table
        :param table: table to delete
        :param sql_filter: filter to search
        :return: operation status
        """

        t = sqlalchemy.text('DELETE FROM {} WHERE {}'.format(table, sql_filter))
        t.execution_options(autocommit=True)
        self.conn.execute(t)
        return True

    def open_connection(self) :
        """
        Get the connection with database.

        :return: object that represents the connection
        """
        engine = sqlalchemy.create_engine(self.connection_database,
                                          connect_args={'check_same_thread': False})
        conn = engine.connect()
        return conn, engine
