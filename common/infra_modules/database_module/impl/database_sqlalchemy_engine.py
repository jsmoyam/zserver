import logging
import sqlalchemy

from common.infra_tools.decorators import log_function
from common.infra_modules.database_module import MODULE_NAME
from common.infra_modules.database_module.model_database_module import DatabaseException
from common.infra_modules.database_module.impl.database_meta import MetaDatabase
from common.infra_modules.database_module.impl.database_generic import DatabaseGeneric

# Get the module logger
logger = logging.getLogger(MODULE_NAME)


class DatabaseSqlAlchemyEngine(MetaDatabase, DatabaseGeneric):
    """
    Class to define the specific implementation of sql alchemy with engine
    """

    def __init__(self, connection_database: str, isolation_level: str):
        """
        Constructor with connection string

        :param connection_database: url connection from ini file
        :param isolation_level: isolation level
        """

        # Init the metaclass
        MetaDatabase.__init__(self, connection_database, isolation_level)

        try:
            # Connect with database
            conn, engine = self.open_connection()
            self.conn = conn
            self.engine = engine
        except DatabaseException as e:
            raise e

    @log_function(logger, logging.DEBUG)
    def exec_query(self, query: str) -> list:
        """
        Execute query passed by parameter

        :param query: query to exec

        :return: list with dictionaries
        :rtype: list
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
        :rtype: bool
        """

        columns = ','.join(['"{}"'.format(x) for x in data.keys()])
        values = ','.join(['"{}"'.format(x) for x in data.values()])

        t = sqlalchemy.text('INSERT INTO {} ({}) VALUES ({})'.format(table, columns, values))
        t.execution_options(autocommit=True)
        self.conn.execute(t)

        return True

    @log_function(logger, logging.DEBUG)
    def read(self, table: str, sql_filter: str = '') -> list:
        """
        Read rows in table with optional filter

        :param table: table to read
        :param sql_filter: filter to select

        :return: row list
        :rtype: list
        """

        where_cause = '' if not sql_filter else 'WHERE {}'.format(sql_filter)
        t = sqlalchemy.text('SELECT * FROM {} {}'.format(table, where_cause))
        rs = self.conn.execute(t)
        list_of_rows = list()
        for row in rs:
            row_as_dict = dict(row)
            list_of_rows.append(row_as_dict)

        return list_of_rows

    @log_function(logger, logging.DEBUG)
    def update(self, table: str, data: dict, sql_filter: str = '') -> bool:
        """
        Update rows in table with optional filter

        :param table: table to update
        :param data: data to update
        :param sql_filter: filter to search

        :return: operation status
        :rtype: bool
        """

        values = ','.join(['{}="{}"'.format(k, v) for k, v in data.items()])

        where_cause = '' if not sql_filter else 'WHERE {}'.format(sql_filter)
        t = sqlalchemy.text('UPDATE {} SET {} {}'.format(table, values, where_cause))
        t.execution_options(autocommit=True)
        self.conn.execute(t)

        return True

    @log_function(logger, logging.DEBUG)
    def delete(self, table: str, sql_filter: str = '') -> bool:
        """
        Delete rows in table with optional filter

        :param table: table to delete
        :param sql_filter: filter to search

        :return: operation status
        :rtype: bool
        """

        where_cause = '' if not sql_filter else 'WHERE {}'.format(sql_filter)
        t = sqlalchemy.text('DELETE FROM {} WHERE {}'.format(table, where_cause))
        t.execution_options(autocommit=True)
        self.conn.execute(t)

        return True

    def open_connection(self):
        """
        Get the connection with database.

        :return: object that represents the connection
        :rtype: conn, engine
        """

        engine = sqlalchemy.create_engine(self.connection_database, isolation_level=self.isolation_level)
        conn = engine.connect()
        return conn, engine

    def get_connection(self):
        """
        Return the connection with database.

        :return: engine, conn
        :rtype: engine, conn
        """

        return self.engine, self.conn
