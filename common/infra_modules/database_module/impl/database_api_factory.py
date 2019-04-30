from common.infra_modules.database_module.model_database import DatabaseException, ErrorMessages
from common.infra_modules.database_module.impl.database_api import DatabaseApi
from common.infra_modules.database_module.impl.database_sqlalchemy import DatabaseSqlAlchemy


class DatabaseApiFactory:
    """
    Class to get any implement
    """

    # Static access to implemented class
    _db = None

    @staticmethod
    def get_connection(orm_type: str, connection_database: str) -> DatabaseApi:
        """
        Get orm database implementation

        :param orm_type: name of implementation software
        :param connection_database: url connection
        """

        if DatabaseApiFactory._db is None:
            DatabaseApiFactory._db = DatabaseApiFactory._implement(orm_type, connection_database)
        return DatabaseApiFactory._db

    @staticmethod
    def _implement(orm_type: str, connection_database: str) -> DatabaseApi:
        """
        Set implementation

        :param orm_type: name of implemented software
        :param connection_database: url connection
        """

        if orm_type == 'sqlalchemy':
            return DatabaseSqlAlchemy(connection_database)
        else:
            raise DatabaseException(ErrorMessages.CONFIGURATION_ERROR)
