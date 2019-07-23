import logging
import sqlalchemy

from sqlalchemy.orm import sessionmaker

from common.infra_tools.decorators import log_function
from common.infra_modules.database_module import MODULE_NAME
from common.infra_modules.database_module.model_database_module import DatabaseException
from common.infra_modules.database_module.impl.database_meta import MetaDatabase
from common.infra_modules.database_module.impl.database_generic import DatabaseGeneric

# Get the module logger
logger = logging.getLogger(MODULE_NAME)


class DatabaseSqlAlchemySession(MetaDatabase, DatabaseGeneric):
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
            engine, session = self.open_connection()
            self.engine = engine
            self.session = session
        except DatabaseException as e:
            raise e

    @log_function(logger, logging.DEBUG)
    def exec_query(self, query: str) -> list:
        pass

    @log_function(logger, logging.DEBUG)
    def insert(self, obj: object) -> bool:
        """
        Insert row in table

        :param obj: object to insert

        :return: operation status
        :rtype: bool
        """

        self.session.add(obj)
        self.session.commit()

        return True

    @log_function(logger, logging.DEBUG)
    def read(self, *args, **kwargs) -> list:
        """
        Read rows in table with optional filter

        :param args: class attributes to read
        :param kwargs: optional arguments

        :return: the object(s) searched
        :rtype: list
        """

        result = self.session.query(*args).filter_by(**kwargs).all()
        return result[0] if len(result) == 1 else result

    @log_function(logger, logging.DEBUG)
    def update(self, obj: object) -> bool:
        """
        Update row in table

        :param obj: object to update

        :return: operation status
        :rtype: bool
        """

        self.session.commit()

        return True

    @log_function(logger, logging.DEBUG)
    def update_query(self, cls: object, values: dict, **kwargs) -> bool:
        """
        Update rows in table with a query

        :param cls: class object to update
        :param values: new values
        :param kwargs: optional arguments

        :return: operation status
        :rtype: bool
        """

        self.session.query(cls).filter_by(**kwargs).update(values)
        self.session.commit()

        return True

    @log_function(logger, logging.DEBUG)
    def delete(self, obj: object) -> bool:
        """
        Delete row in table

        :param obj: object to delete

        :return: operation status
        :rtype: bool
        """

        self.session.delete(obj)
        self.session.commit()

        return True

    @log_function(logger, logging.DEBUG)
    def delete_query(self, cls: object, **kwargs) -> bool:
        """
        Delete row in table with a query

        :param cls: object to delete
        :param kwargs: optional arguments

        :return: operation status
        :rtype: bool
        """

        self.session.query(cls).filter_by(**kwargs).delete()
        self.session.commit()

        return True

    def open_connection(self):
        """
        Get the connection with database.

        :return: object that represents the connection
        :rtype: conn, engine
        """

        engine = sqlalchemy.create_engine(self.connection_database, isolation_level=self.isolation_level)
        session = sessionmaker(bind=engine)
        return engine, session()

    def get_connection(self):
        """
        Return the connection with database.

        :return: engine, conn
        :rtype: engine, conn
        """

        return self.engine, self.session
