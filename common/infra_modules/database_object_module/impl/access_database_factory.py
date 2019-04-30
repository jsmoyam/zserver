from common.infra_modules.database_object_module.data_model import DatabaseObjectException, ErrorMessages
from common.infra_modules.database_object_module.impl.access_database import AccessDatabase
from common.infra_modules.database_object_module.impl.access_database_mongodb import AccessDatabaseMongoDB


class AccessDatabaseFactory:
    """
    Class to get any implement of the database
    """

    # Static access to implemented database
    _access_database = None

    @staticmethod
    def get_access_database(name_database: str, connection_database: str) -> AccessDatabase:
        """
        Get database connection

        :param name_database: name of implemented database
        :type name_database: str

        :param connection_database: url connection
        :type connection_database: str

        :return: connection to database
        :rtype: AccessDatabase
        """

        if AccessDatabaseFactory._access_database is None:
            AccessDatabaseFactory._access_database = AccessDatabaseFactory._implement_database(name_database,
                                                                                               connection_database)
        return AccessDatabaseFactory._access_database

    @staticmethod
    def _implement_database(name_database: str, connection_database: str) -> AccessDatabase:
        """
        Set implemented database

        :param name_database: name of implemented database
        :type name_database: str

        :param connection_database: url connection
        :type connection_database: str

        :return: instance of implemented database
        :rtype: AccessDatabase
        """

        if name_database == 'mongodb':
            return AccessDatabaseMongoDB(connection_database)
        else:
            raise DatabaseObjectException(ErrorMessages.CONFIGURATION_ERROR)
