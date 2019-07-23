from common.infra_modules.database_module.impl.database_meta import MetaDatabase
from common.infra_modules.database_module.impl.database_sqlalchemy_engine import DatabaseSqlAlchemyEngine
from common.infra_modules.database_module.impl.database_sqlalchemy_session import DatabaseSqlAlchemySession
from common.infra_modules.database_module.model_database_module import DatabaseErrorCode, DatabaseException


class DatabaseFactory:
    """
    Class to get a database's implementation
    """

    # Static access to implemented class
    _db = None

    @staticmethod
    def get_connection(orm_type: str, connection_database: str, isolation_level: str) -> MetaDatabase:
        """
        Get orm database implementation

        :param orm_type: name of implementation software
        :param connection_database: url connection
        :param isolation_level: isolation level
        """

        if DatabaseFactory._db is None:
            DatabaseFactory._db = DatabaseFactory._implement(orm_type, connection_database, isolation_level)
        return DatabaseFactory._db

    @staticmethod
    def _implement(orm_type: str, connection_database: str, isolation_level: str) -> MetaDatabase:
        """
        Set implementation

        :param orm_type: name of implemented software
        :param connection_database: url connection
        :param isolation_level: isolation level
        """

        if orm_type == 'sqlalchemy':
            return DatabaseSqlAlchemySession(connection_database, isolation_level)
        elif orm_type == 'sqlalchemy_engine':
            return DatabaseSqlAlchemyEngine(connection_database, isolation_level)
        else:
            raise DatabaseException(DatabaseErrorCode.DATABASE_CONFIGURATION_ERROR)
