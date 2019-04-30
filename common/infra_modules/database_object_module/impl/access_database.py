import abc


class AccessDatabase:
    """
    Abstract class to define the function header of all the access implementations to the different databases.
    """

    __metaclass__ = abc.ABCMeta

    # Field _id
    ID_FIELD = '_identifier'

    # Field _timestamp
    TIMESTAMP_FIELD = '_timestamp'

    # Field _deleted_count
    DELETED_COUNT = '_deleted_count'

    # Field _deleted_count
    UPDATED_COUNT = '_updated_count'

    # Separator between schema and sub_schema
    SEPARATOR = '_'

    # Suffix for storing index
    INDEX_ATTR = 'index'

    def __init__(self, connection_url: str) -> None:
        """
        Builder method of the class.

        :param connection_url: name of the connection with the database
        :type connection_url: str

        :return: this function return nothing
        :rtype: None
        """

        self.connection = None
        self.connection_url = connection_url

    @abc.abstractmethod
    def get(self, schema: str, conditions: list, criteria: str, native_criteria: bool) -> list:
        """
        Get the object from the database.

        :param schema: name of schema of the database
        :type schema: str

        :param conditions: conditions to update the object (list of tuples)
        :type conditions: list

        :param criteria: advanced condition for complex searches, can be native or generic
        :type criteria: str

        :param native_criteria: select between native criteria or generic criteria
        :type native_criteria: bool

        :return: list of objects gotten as a dictionary
        :rtype: list of dictionary

        """
        pass

    @abc.abstractmethod
    def put(self, schema: str, data: dict) -> list:
        """
        Put the object into the database.

        :param schema: name of schema of the database
        :type schema: str

        :param data: dict of objects to put into the database
        :type data: dict

        :return: list with inserted _id
        :rtype: list of dictionary
        """

        pass

    @abc.abstractmethod
    def update(self, schema: str, data: dict, conditions: list, criteria: str, native_criteria: bool) -> list:
        """
        Update the object from the database.

        :param schema: name of schema of the database
        :type schema: str

        :param data: list of objects to update into the database
        :type data: list

        :param conditions: conditions to update the object (list of tuples)
        :type conditions: list

        :param criteria: advanced condition for complex searches, can be native or generic
        :type criteria: str

        :param native_criteria: select between native criteria or generic criteria
        :type native_criteria: bool

        :return: number of updated elements in a list of dictionary
        :rtype: list of dictionary
        """

        pass

    @abc.abstractmethod
    def remove(self, schema: str, conditions: list, criteria: str, native_criteria: bool) -> list:
        """
        Remove the objects from the database.

        :param schema: name of schema of the database
        :type schema: str

        :param conditions: conditions to update the object (list of tuples)
        :type conditions: list

        :param criteria: advanced condition for complex searches, can be native or generic
        :type criteria: str

        :param native_criteria: select between native criteria or generic criteria
        :type native_criteria: bool

        :return: number of removed elements in a list of dictionary
        :rtype: list of dictionary
        """

        pass

    @abc.abstractclassmethod
    def open_connection(self) -> None:
        pass

    @abc.abstractclassmethod
    def close_connection(self) -> None:
        pass

    @abc.abstractclassmethod
    def check_connection(self) -> bool:
        """
        Check that the connection is alive.

        :return:
        :rtype: None
        """

        pass

    @abc.abstractclassmethod
    def get_last_index(self, schema: str, sub_schema: str) -> int:
        """
        Returns index as int of schema_collection
        :param schema: schema to search
        :param sub_schema: sub_schema to search
        :return: int
        """

        pass

    @abc.abstractclassmethod
    def update_index(self, schema_collection_index: str, value: int) -> None:
        """
        Update index in datastore
        :param schema_collection_index: schema to update index
        :param value: value of index
        :return: none, exception if error
        """

        pass


    @staticmethod
    def get_schema_collection(schema: str, sub_schema: str) -> str:
        return schema + AccessDatabase.SEPARATOR + sub_schema

    @staticmethod
    def get_schema_collection_index(schema: str, sub_schema: str) -> str:
        return schema + AccessDatabase.SEPARATOR + sub_schema + AccessDatabase.SEPARATOR + AccessDatabase.INDEX_ATTR
