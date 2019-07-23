import abc


class MetaDatabase:
    """
    Abstract class to define the function header of all the access implementations.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, connection_database: str, isolation_level: str):
        """
        Constructor: Set the connection database
        """

        self.connection_database = connection_database
        self.isolation_level = isolation_level

    @abc.abstractmethod
    def exec_query(self, query: str) -> list:
        """
        Execute the query passed by parameter

        :param query: query to exec
        :return: list with data
        """

        pass

    @abc.abstractmethod
    def insert(self, table: str, data: dict) -> bool:
        """
        Insert row in table

        :param table: table to insert
        :param data: data to insert

        :return: operation status
        :rtype: bool
        """

        pass

    @abc.abstractmethod
    def read(self, table: str, sql_filter: str) -> list:
        """
        Read rows in table with optional filter

        :param table: table to read
        :param sql_filter: filter to select

        :return: row list
        :rtype: list
        """

        pass

    @abc.abstractmethod
    def update(self, table: str, data: dict, sql_filter: str) -> bool:
        """
        Update rows in table

        :param table: table to update
        :param data: data to update
        :param sql_filter: filter to search

        :return: operation status
        :rtype: bool
        """

        pass

    @abc.abstractmethod
    def delete(self, table: str, sql_filter: str) -> bool:
        """
        Delete rows in table

        :param table: table to delete
        :param sql_filter: filter to search

        :return: operation status
        :rtype: bool
        """

        pass
