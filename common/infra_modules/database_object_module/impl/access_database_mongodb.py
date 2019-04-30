import logging

from pymongo import MongoClient, collection, errors, ASCENDING
from pymongo.errors import ServerSelectionTimeoutError

from common.infra_tools.decorators import log_function
from common.infra_modules.database_object_module import MODULE_NAME
from common.infra_modules.database_object_module.data_model import DatabaseObjectException, ErrorMessages
from common.infra_modules.database_object_module.impl.access_database import AccessDatabase

logger = logging.getLogger(MODULE_NAME)


class AccessDatabaseMongoDB(AccessDatabase):
    """
    Class to define the specific access to the MongoDB database.
    """

    # Operators
    MONGO_OPERATORS = {
        '=': '$eq', '>': '$gt', '>=': '$gte', 'in': '$in', '<': '$lt', '<=': '$lte', '!=': '$ne', 'out': '$nin'
    }

    # Mongo join condition
    MONGO_JOIN_CONDITION = '$and'

    # Mongo update operators
    MONGO_UPDATE_OPERATOR = '$set'

    # Mongo ObjectId field
    OBJECT_ID_FIELD = '_id'

    def __init__(self, connection_url: str) -> None:
        """
        Constructor with url connection

        :param connection_url: url connection from ini file
        :type connection_url: str

        :return: This function return nothing
        :rtype: None
        """

        # Init the father class
        AccessDatabase.__init__(self, connection_url)

        try:
            # Connect with mongodb
            self.open_connection()

            # Get database from URL connection
            self.db = self.connection.get_database()

            # Initialize caches
            self.cache_collections = dict()

        except errors.ConfigurationError:
            raise DatabaseObjectException(ErrorMessages.CONFIGURATION_ERROR)
        except DatabaseObjectException as e:
            raise e

    @log_function(logger, logging.DEBUG)
    def get(self, schema: str, conditions: list, criteria: str, native_criteria: bool) -> list:
        """
        Get data from mongodb

        :param schema: schema (name of collection in mongodb)
        :type schema: str

        :param conditions: conditions to search (list of tuple)
        :type conditions: list

        :param criteria: criteria from mongodb
        :type criteria: str

        :param native_criteria: boolean for search by native criteria from mongodb
        :type native_criteria: bool

        :return: list of dictionary with data
        :rtype: list
        """

        # Create the output list
        output_list = list()

        try:
            # Get collection
            mongo_collect = self._get_collection(schema)

            # Get criteria in mongodb language
            mongo_criteria = AccessDatabaseMongoDB._create_mongo_criteria(conditions, criteria, native_criteria)

            # Find data with criteria
            mongo_result = mongo_collect.find(mongo_criteria).sort(AccessDatabase.TIMESTAMP_FIELD)

            # For each data: recover _id, set to data and add to output list
            for element in mongo_result:
                del element[AccessDatabaseMongoDB.OBJECT_ID_FIELD]
                output_list.append(element)

            # Return the list with the updated elements
            return output_list

        except ServerSelectionTimeoutError:
            raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)
        except Exception:
            raise DatabaseObjectException(ErrorMessages.GET_ERROR)

    @log_function(logger, logging.DEBUG)
    def put(self, schema: str, data: dict) -> list:
        """
        Insert data to mongodb

        :param schema: schema (name of collection in mongodb)
        :type schema: str

        :param data: data to store in dictionary format
        :type data: dict

        :return: list of dictionary with inserted _id
        :rtype: list
        """

        # Create the output list
        output_list = list()

        try:
            # Get collection creating it if not exists
            mongo_collect = self._get_collection(schema, create_collection=True)

            # Insert data and recover _id
            mongo_collect.insert_one(data)

            output_list.append({AccessDatabase.ID_FIELD: data[AccessDatabase.ID_FIELD]})

            # Return the list with the updated elements
            return output_list

        except ServerSelectionTimeoutError:
            raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)
        except Exception:
            raise DatabaseObjectException(ErrorMessages.PUT_ERROR)

    @log_function(logger, logging.DEBUG)
    def update(self, schema: str, data: dict, conditions: list, criteria: str,
               native_criteria: bool) -> list:
        """
        Update data in mongodb

        :param schema: schema (name of collection in mongodb)
        :type schema: str

        :param data: data to store in dictionary format
        :type data: dict

        :param conditions: conditions to search (list of tuple)
        :type conditions: list

        :param criteria: criteria from mongodb
        :type criteria: str

        :param native_criteria: boolean for search by native criteria from mongodb
        :type native_criteria: bool

        :return: list of dictionary with number of updated elements
        :rtype: list
        """

        # Create the output list
        output_list = list()

        try:
            # Get collection from mongodb
            mongo_collect = self._get_collection(schema)

            # Define data to update
            mongo_data_update = {AccessDatabaseMongoDB.MONGO_UPDATE_OPERATOR: data}

            # Get criteria in mongodb language
            mongo_criteria = AccessDatabaseMongoDB._create_mongo_criteria(conditions, criteria, native_criteria)

            # Update elements and recover number of updated elements and number of matched elements
            mongo_result = mongo_collect.update_many(mongo_criteria, mongo_data_update)
            modified_count = mongo_result.modified_count

            # Add number of updated elements
            output_list.append({AccessDatabase.UPDATED_COUNT: modified_count})

            # Return the list with the updated elements
            return output_list

        except ServerSelectionTimeoutError:
            raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)
        except Exception:
            raise DatabaseObjectException(ErrorMessages.PUT_ERROR)

    @log_function(logger, logging.DEBUG)
    def remove(self, schema: str, conditions: list, criteria: str, native_criteria: bool) -> list:
        """
        Delete elements from mongodb

        :param schema: schema (name of collection in mongodb)
        :type schema: str

        :param conditions: conditions to search (list of tuple)
        :type conditions: list

        :param criteria: criteria from mongodb
        :type criteria: str

        :param native_criteria: boolean for search by native criteria from mongodb
        :type native_criteria: bool

        :return: list of dictionary with number of deleted elements
        :rtype: list
        """

        # Create the output list
        output_list = list()

        try:
            # Get collection from mongodb
            mongo_collect = self._get_collection(schema)

            # Get criteria in mongodb language
            mongo_criteria = AccessDatabaseMongoDB._create_mongo_criteria(conditions, criteria, native_criteria)

            # Delete elements with criteria and recover number of deleted elements
            mongo_result = mongo_collect.delete_many(mongo_criteria)
            deleted_count = mongo_result.deleted_count

            # Add number of deleted elements
            output_list.append({AccessDatabase.DELETED_COUNT: deleted_count})

            # Return the list with removed elements.
            return output_list

        except ServerSelectionTimeoutError:
            raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)
        except Exception as e:
            # If there is SCHEMA_ERROR, this is not an error because schema does not exist. Only log warning
            if str(e) == ErrorMessages.SCHEMA_ERROR:
                logger.warning('Schema or subschema does not exist')
                output_list.append({AccessDatabase.DELETED_COUNT: 0})
                return output_list
            else:
                raise DatabaseObjectException(ErrorMessages.REMOVE_ERROR)

    def _get_collection(self, schema: str, create_collection: bool = False, create_index: bool = True) \
            -> collection.Collection:
        """
        Get collection from database

        :param schema: collection of mongodb
        :type schema: str

        :param create_collection: create collection or not
        :type create_collection: bool

        :return: collection from mongodb
        :rtype: collection
        """

        # If collection exists, get it.
        if schema in self.cache_collections.keys():
            mongo_collect = self.cache_collections[schema]

        # If not, if collection is in mongodb, get and cache
        elif schema in self.db.collection_names():
            mongo_collect = self.db[schema]
            self.cache_collections[schema] = mongo_collect

        # If not, if the function can create it, create it
        elif create_collection:
            mongo_collect = self.db.create_collection(schema)
            if create_index:
                mongo_collect.create_index([(AccessDatabase.TIMESTAMP_FIELD, ASCENDING)],
                                           name=AccessDatabase.TIMESTAMP_FIELD, unique=True)
                mongo_collect.create_index([(AccessDatabase.ID_FIELD, ASCENDING)],
                                           name=AccessDatabase.ID_FIELD, unique=True)
            self.cache_collections[schema] = mongo_collect

        # In other case, throw the exception
        else:
            logger.warning('Mongodb schema {} can not be recovered'.format(schema))
            raise DatabaseObjectException(ErrorMessages.SCHEMA_ERROR)

        # Return the mongo collection
        return mongo_collect

    def open_connection(self) -> None:
        """
        Get the connection whith mongodb and check that it is successful.

        :return: object that represents the connection
        :rtype: object
        """

        try:
            self.connection = MongoClient(self.connection_url)
            self.connection.is_mongos

        except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError):
            raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)

    def close_connection(self) -> None:
        self.connection.close()

    def check_connection(self) -> bool:
        """
        Check that the connection with mongodb is alive, try to connect if not.

        :return: true if the connection is alive, false if not
        :rtype: bool
        """

        try:
            # Check the connection by checking the databases
            self.connection.list_database_names()

            # Return true, the connection is alive
            return True

        except errors.ConnectionFailure:
            # Return false, the connection is dead
            logger.debug('Mongodb connection is dead', exc_info=True)
            return False

    def get_last_index(self, schema: str, sub_schema: str) -> int:
        """
        Recover last index from all collections
        :param schema: schema to search
        :param sub_schema: sub_schema to search
        :return: last inserted index of schema_collection
        """

        schema_collection = self.get_schema_collection(schema, sub_schema)
        schema_collection_index = self.get_schema_collection_index(schema, sub_schema)

        try:
            # Recover collections. Add collection to cache if not exists
            collection_index = self._get_collection(schema_collection_index, create_collection=True, create_index=False)
            collection_data = self._get_collection(schema_collection, create_collection=True)

            # Find last data inserted from data collection
            sort_filter = '{' + AccessDatabaseMongoDB.OBJECT_ID_FIELD + ':-1}'
            mongo_result = collection_data.find({}).sort(sort_filter).limit(1)
            result = [element[AccessDatabase.ID_FIELD] for element in mongo_result]
            identifier_collection = 0 if len(result) == 0 else result[0]

            # Find last index inserted from index collection
            mongo_result = collection_index.find({})
            result = [element[AccessDatabase.ID_FIELD] for element in mongo_result]
            identifier_collection_index = 0 if len(result) == 0 else result[0]

            return max(identifier_collection, identifier_collection_index)

        except ServerSelectionTimeoutError:
            raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)
        except Exception:
            raise DatabaseObjectException(ErrorMessages.GET_INDEX_ERROR)

    def update_index(self, schema_collection_index: str, value: int) -> None:

        try:
            # Get collection from mongodb
            mongo_collect = self._get_collection(schema_collection_index, create_collection=True, create_index=False)

            # Define data to update
            mongo_data = {AccessDatabase.ID_FIELD: value}
            mongo_data_update = {AccessDatabaseMongoDB.MONGO_UPDATE_OPERATOR: mongo_data}

            # Update all elements of collection index
            mongo_collect.update_many({}, mongo_data_update, upsert=True)

        except ServerSelectionTimeoutError:
            raise DatabaseObjectException(ErrorMessages.CONNECTION_ERROR)
        except Exception:
            raise DatabaseObjectException(ErrorMessages.UPDATE_INDEX_ERROR)

    @staticmethod
    def _create_mongo_criteria(conditions: list, criteria: str, native_criteria: bool) -> dict:
        """
        Create criteria native of mongodb

        :param conditions: list of tuple of conditions
        :type conditions: list

        :param criteria: native criteria language from mongodb
        :type criteria: str

        :param native_criteria: bool for use native criteria or not
        :type native_criteria: bool

        :return: filter
        :rtype: dict
        """

        # Create a filter with list of empty conditions
        mongo_criteria = {AccessDatabaseMongoDB.MONGO_JOIN_CONDITION: list()}

        try:
            # Iterate all conditions to create native mongodb filter
            for condition in conditions:

                # Special case if the variable is the ID
                if condition[0] == AccessDatabase.ID_FIELD:

                    # If the value to compare is a list, one list of ObjectId must be generated
                    if isinstance(condition[2], (list, tuple)):
                        filter_condition = {
                            condition[0]: {AccessDatabaseMongoDB.MONGO_OPERATORS[condition[1]]: conditions[2]}
                        }

                    # If the value is zero, negative or None, all elements must be recovered
                    elif condition[2] is None or condition[2] <= 0:
                        filter_condition = {}

                    # Else the ObjectId  must be generated
                    else:
                        filter_condition = {
                            condition[0]: {AccessDatabaseMongoDB.MONGO_OPERATORS[condition[1]]: condition[2]}
                        }

                # The rest of the variables do not have special cases
                else:
                    value_compare = condition[2]
                    filter_condition = {
                        condition[0]: {AccessDatabaseMongoDB.MONGO_OPERATORS[condition[1]]: value_compare}
                    }

                # Add condition translated to mongodb filter language
                mongo_criteria[AccessDatabaseMongoDB.MONGO_JOIN_CONDITION].append(filter_condition)

            # Only if native criteria is active, add native from user
            if native_criteria and len(criteria) > 0:
                mongo_criteria[AccessDatabaseMongoDB.MONGO_JOIN_CONDITION].append(dict(criteria))

            # Return the mongo criteria
            logger.debug('Mongo criteria {}'.format(mongo_criteria))
            return mongo_criteria

        except Exception:
            raise DatabaseObjectException(ErrorMessages.CRITERIA_ERROR)
