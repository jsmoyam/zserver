import abc


class DatabaseApi:
    """
    Abstract class to define the function header of all the access implementations.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, connection_database: str):
        """
        Builder method of the class.
        """

        self.connection_database = connection_database

    @abc.abstractmethod
    def exec_query(self, query: str) -> list:
        """
        Execute query
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
        """
        pass

    @abc.abstractmethod
    def read(self, table: str, sql_filter: str) -> list:
        """
        Read rows in table with filter
        :param table: table to read
        :param sql_filter: filter to select
        :return: row list
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
        """
        pass

    @abc.abstractmethod
    def delete(self, table: str, sql_filter: str) -> bool:
        """
        Delete rows in table
        :param table: table to delete
        :param sql_filter: filter to search
        :return: operation status
        """
        pass
