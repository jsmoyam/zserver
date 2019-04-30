import time

from common import config
from common.infra_modules.infra_module import InfraModule
from common.infra_tools.decorators import log_function
from common.infra_tools.task_thread import TaskThread
from common.infra_modules.database_object_module import MODULE_NAME
from common.infra_modules.database_object_module.data_model import DatabaseObjectResult, DatabaseObjectException, ErrorMessages, \
    DatabaseObject
from common.infra_modules.database_object_module.impl.access_database import AccessDatabase
from common.infra_modules.database_object_module.impl.access_database_factory import AccessDatabaseFactory


logger = config.get_log(MODULE_NAME)


class DatabaseObjectModule(InfraModule):
    """
    Main class of database access
    """

    def initialize(self):
        """
        Get configuration, database name and connection instance
        """

        try:
            self.use_cache = self.module_config.get_value(MODULE_NAME, 'use_cache')
            name_database = self.module_config.get_value(MODULE_NAME, 'name_database')
            connection_database = self.module_config.get_value(MODULE_NAME, 'connection_database')

            # Connect to datastore
            self.access_db = AccessDatabaseFactory.get_access_database(name_database, connection_database)
            self.is_connected = True

            # Index cache. This variable has index data reading last objects inserted (or last index if there are not
            # data in collection) when inserting data
            self.cache_index = dict()

            # Data cache

            logger.info('Datastore connected')

        except DatabaseObjectException:
            logger.error('Error opening connection to datastore', exc_info=True)
            self.is_connected = False

        self.daemon = CheckConnectionThread(self)
        self.daemon.start()
        logger.info('CheckConnection daemon started')
        logger.info('Accepting requests')

    def exit(self) -> None:
        self.daemon.shutdown()
        logger.info('SHUTDOWN MODULE')

    @log_function(logger)
    def get(self, schema: str, sub_schema: str, conditions: list = ((AccessDatabase.ID_FIELD, '!=', None),),
            criteria: str = '', native_criteria: bool = False) -> DatabaseObjectResult:
        """
        Get data from data store

        :param schema: connection schema
        :type schema: str

        :param sub_schema: object type to save
        :type sub_schema: str

        :param conditions: list of tuple conditions
        :type conditions: list

        :param criteria: criteria search
        :type criteria: str

        :param native_criteria: criteria native from database
        :type native_criteria: bool

        :return: database object result
        :rtype: DatabaseObjectResult
        """

        try:
            # Check if database is up
            if not self.is_connected:
                logger.error('Error opening connection to datastore', exc_info=True)
                raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)

            schema_collection = AccessDatabase.get_schema_collection(schema, sub_schema)
            ret = self.access_db.get(schema_collection, conditions, criteria, native_criteria)
            return DatabaseObjectModule._get_data_object_result_from_json('get', result=ret)

        except DatabaseObjectException as e:

            # Set false only if socket timeout exception and if another process has not set it to false
            if str(e) == ErrorMessages.CONNECTION_ERROR and self.is_connected:
                self.is_connected = False
                logger.critical('Connection to datastore lost')

            logger.error('Error recovering data from datastore', exc_info=True)
            return DatabaseObjectModule._get_data_object_result_from_json('get', exception=e)

    @log_function(logger)
    def put_object(self, schema: str, sub_schema: str, data: DatabaseObject) -> DatabaseObjectResult:
        """
        Write object to object store

        :param schema: connection schema
        :type schema: str

        :param sub_schema: object type to save
        :type sub_schema: str

        :param data: data to save
        :type data: DatabaseObject

        :return: database object result with _id
        :rtype: DatabaseObjectResult
        """

        # Validate data, checking that has inheritance from DatabaseObject
        if not issubclass(data.__class__, DatabaseObject):
            e = DatabaseObjectException(ErrorMessages.INHERITANCE_ERROR)
            return DatabaseObjectModule._get_data_object_result_from_json('put', exception=e)

        return self.put(schema, sub_schema, data.__dict__)

    @log_function(logger)
    def put(self, schema: str, sub_schema: str, data: dict) -> DatabaseObjectResult:
        """
        Write object to object store

        :param schema: connection schema
        :type schema: str

        :param sub_schema: object type to save
        :type sub_schema: str

        :param data: data to save
        :type data: dict

        :return: database object result with _id
        :rtype: DatabaseObjectResult
        """

        try:
            # Check if database is up
            if not self.is_connected:
                logger.error('Error opening connection to datastore', exc_info=True)
                raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)

            # Validate data, checking that object has mandatory fields
            self._validate_data(data)

            # Recover collection joining schema and sub_schema, same for index
            schema_collection = AccessDatabase.get_schema_collection(schema, sub_schema)
            schema_collection_index = AccessDatabase.get_schema_collection_index(schema, sub_schema)

            # Get next index and set index to data
            next_index = self._get_next_index(data, schema, sub_schema)
            data[AccessDatabase.ID_FIELD] = next_index

            # Set timestamp attribute
            data[AccessDatabase.TIMESTAMP_FIELD] = int(time.time() * 10000000)

            ret = self.access_db.put(schema_collection, data)

            # Update cache index
            self.cache_index[schema_collection_index] = next_index
            self.access_db.update_index(schema_collection_index, next_index)

            return DatabaseObjectModule._get_data_object_result_from_json('put', result=ret)

        except DatabaseObjectException as e:

            # Set false only if socket timeout exception and if another process has not set it to false
            if str(e) == ErrorMessages.CONNECTION_ERROR and self.is_connected:
                self.is_connected = False
                logger.critical('Connection to datastore lost')

            logger.error('Error inserting data to datastore', exc_info=True)
            return DatabaseObjectModule._get_data_object_result_from_json('put', exception=e)

    @log_function(logger)
    def update_object(self, schema: str, sub_schema: str, data: DatabaseObject,
                      conditions: list = ((AccessDatabase.ID_FIELD, '!=', None),), criteria: str = '',
                      native_criteria: bool = False) -> DatabaseObjectResult:
        """
        Update data in object store. This method will update all object data defined in "data" attribute

        :param schema: connection schema
        :type schema: str

        :param sub_schema: object type to save
        :type sub_schema: str

        :param data: data to update
        :type data: DatabaseObject

        :param conditions: list of tuple conditions
        :type conditions: list

        :param criteria: criteria to search
        :type criteria: str

        :param native_criteria: use native criteria from database or not
        :type native_criteria: bool

        :return: data object result wit number of updated objects
        :rtype: DatabaseObjectResult
        """

        # Validate data, checking that has inheritance from DatabaseObject
        if not issubclass(data.__class__, DatabaseObject):
            e = DatabaseObjectException(ErrorMessages.INHERITANCE_ERROR)
            return DatabaseObjectModule._get_data_object_result_from_json('update', exception=e)

        # This updates all object data defined in "data" attribute because we pass __dict__ to update method
        return self.update(schema, sub_schema, data.__dict__, conditions, criteria, native_criteria)

    @log_function(logger)
    def update(self, schema: str, sub_schema: str, data: dict,
               conditions: list = ((AccessDatabase.ID_FIELD, '!=', ''),),
               criteria: str = '', native_criteria: bool = False) -> DatabaseObjectResult:
        """
        Update data in object store. . This method will update only fields defined in "data" attribute

        :param schema: connection schema
        :type schema: str

        :param sub_schema: object type to save
        :type sub_schema: str

        :param data: data to update
        :type data: dict

        :param conditions: list of tuple conditions
        :type conditions: list

        :param criteria: criteria to search
        :type criteria: str

        :param native_criteria: use native criteria from database or not
        :type native_criteria: bool

        :return: data object result wit number of updated objects
        :rtype: DatabaseObjectResult
        """

        try:
            # Check if database is up
            if not self.is_connected:
                logger.error('Error opening connection to datastore', exc_info=True)
                raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)

            # Delete all private attributes. It is forbidden to modify this attributes
            del data[AccessDatabase.ID_FIELD]
            del data[AccessDatabase.TIMESTAMP_FIELD]
            del data[AccessDatabase.UPDATED_COUNT]
            del data[AccessDatabase.DELETED_COUNT]

            schema_collection = AccessDatabase.get_schema_collection(schema, sub_schema)
            ret = self.access_db.update(schema_collection, data, conditions, criteria, native_criteria)

            return DatabaseObjectModule._get_data_object_result_from_json('update', result=ret)

        except DatabaseObjectException as e:

            # Set false only if socket timeout exception and if another process has not set it to false
            if str(e) == ErrorMessages.CONNECTION_ERROR and self.is_connected:
                self.is_connected = False
                logger.critical('Connection to datastore lost')

            logger.error('Error updating data from datastore', exc_info=True)
            return DatabaseObjectModule._get_data_object_result_from_json('update', exception=e)

    @log_function(logger)
    def remove(self, schema: str, sub_schema: str, conditions: list = ((AccessDatabase.ID_FIELD, '!=', None),),
               criteria: str = '',
               native_criteria: bool = False) -> DatabaseObjectResult:
        """
        Remove data in object store

        :param schema: connection schema
        :type schema: str

        :param sub_schema: object type to save
        :type sub_schema: str

        :param conditions: list of tuple conditions
        :type conditions: list

        :param criteria: criteria to search
        :type criteria: str

        :param native_criteria: use native criteria from database or not
        :type native_criteria: bool

        :return: data object result wit number of deleted objects
        :rtype: DatabaseObjectResult
        """

        try:
            # Check if database is up
            if not self.is_connected:
                logger.error('Error opening connection to datastore', exc_info=True)
                raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)

            schema_collection = AccessDatabase.get_schema_collection(schema, sub_schema)
            ret = self.access_db.remove(schema_collection, conditions, criteria, native_criteria)
            return DatabaseObjectModule._get_data_object_result_from_json('remove', result=ret)

        except DatabaseObjectException as e:

            # Set false only if socket timeout exception and if another process has not set it to false
            if str(e) == ErrorMessages.CONNECTION_ERROR and self.is_connected:
                self.is_connected = False
                logger.critical('Connection to datastore lost')

            logger.error('Error removing data from datastore', exc_info=True)
            return DatabaseObjectModule._get_data_object_result_from_json('remove', exception=e)

    def _get_next_index(self, data: dict, schema: str, sub_schema: str) -> int:
        """
        Check index of data to insert
        :param data: data to insert
        :param schema: schema to search
        :param sub_schema: sub_schema to search
        :return: next index of the data or exception
        """

        # Recover collection index joining schema and sub_schema
        schema_collection_index = AccessDatabase.get_schema_collection_index(schema, sub_schema)

        # Check that schema_collections exists, and if not then create in cache_index
        if schema_collection_index not in self.cache_index.keys():
            self.cache_index[schema_collection_index] = self.access_db.get_last_index(schema, sub_schema)

        # If not exists _identifier, then create a new _identifier from cache
        # If exists _identifier, then check that is greather than last inserted _identifier. If not then raise excepcion
        if data[AccessDatabase.ID_FIELD] is None:
            next_index = self.cache_index[schema_collection_index] + 1
        else:
            next_index = data[AccessDatabase.ID_FIELD]
            if next_index <= self.cache_index[schema_collection_index]:
                raise DatabaseObjectException(ErrorMessages.INDEX_VALUE_ERROR)

        return next_index

    @staticmethod
    def _validate_data(data: dict) -> None:
        """
        Check of data inherit from DatabaseObject

        :param data: data to check
        :type data: dict

        :return: This function return nothing
        :rtype: None
        """

        if not all(key in data.keys() for key in vars(DatabaseObject())):
            raise DatabaseObjectException(ErrorMessages.INHERITANCE_ERROR)

    @staticmethod
    def _get_data_object_result_from_json(from_method: str, result: list = None,
                                          exception: Exception = None) -> DatabaseObjectResult:
        """
        Convert data from implemented database to data object result
        :param from_method: method which has been executed
        :param result: data returned by method
        :return: database object result with information about output
        """

        # Detected exception. It is convenient to detect all type of exceptions
        if exception is not None:
            return DatabaseObjectResult(DatabaseObjectResult.CODE_KO, msg=str(exception),
                                        exception=exception)

        if list is not None:
            if from_method in ['get', 'remove', 'update', 'put']:
                return DatabaseObjectResult(DatabaseObjectResult.CODE_OK, data=str(result))
            else:
                return DatabaseObjectResult(DatabaseObjectResult.CODE_KO, data='')


class CheckConnectionThread(TaskThread):

    def __init__(self, dom: DatabaseObjectModule) -> None:
        TaskThread.__init__(self)
        self.dom = dom

    def task(self) -> None:
        if self.dom.is_connected:
            return

        logger.critical('Datastore disconnected')
        try:
            self.dom.access_db.close_connection()
            time.sleep(0.05)
            self.dom.access_db.open_connection()
            self.dom.is_connected = self.dom.access_db.check_connection()
            logger.info('Connection restored')
        except DatabaseObjectException:
            logger.critical('Connection can not be restored. Trying ...')
