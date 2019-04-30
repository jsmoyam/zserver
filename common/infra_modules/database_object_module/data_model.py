import ast

from common.infra_modules.infra_exception import InfraException
from common.infra_modules.database_object_module.impl.access_database import AccessDatabase


class DatabaseObject:
    """
    Class of standard data input
    """

    def __init__(self) -> None:
        """
        Constructor without parameters
        """

        # Create internal variables
        self._identifier = None
        self._timestamp = None
        self._deleted_count = 0
        self._updated_count = 0

    def get_identifier(self) -> int:
        """
        Get value of ID variable

        :return: value of ID
        :rtype: int
        """

        # Return the ID
        return self._identifier

    def get_timestamp(self) -> int:
        return self._timestamp

    def get_deleted_count(self) -> int:
        return self._deleted_count

    def get_updated_count(self) -> int:
        return self._updated_count

    def __repr__(self) -> None:
        """
        The function must generate a representation of the object in dictionary format

        :return: This function return nothing
        :rtype: None
        """

        # This method is used for store objects inside objects. The function must return string in dictionary format
        raise NotImplementedError(ErrorMessages.REPR_ERROR)


class DatabaseObjectResult:
    """
    Class of standard data result
    """

    # Module codes
    CODE_OK = 'OK'
    CODE_KO = 'KO'

    def __init__(self, code: str, data: str = '', msg: str = '', exception: Exception = None) -> None:
        self.code_list = (DatabaseObjectResult.CODE_OK, DatabaseObjectResult.CODE_KO)
        self.code = code
        self.data = data
        self.msg = msg
        self.exception = exception

    def get_object_from_data(self, obj=DatabaseObject()) -> list:

        if self.code == self.CODE_KO:
            raise (DatabaseObjectException(ErrorMessages.KO_ERROR))

        # Recover list of dictionaries from string
        datas = ast.literal_eval(self.data)

        # Recover all attributes from obj and get a class except private attrs from python and internal variables
        attrs = [i for i in obj.__dict__.keys() if i[:1] != '_']
        attrs_set = set(attrs)
        cls = obj.__class__

        output = list()
        for data in datas:

            # If user not set the class, then create a DatabaseObject instance and copy values
            # If user set the class, then create an instance of that class and copy values, checking that exist
            #           all attributes
            #     If not exists all attributes, then raise exception
            #     Else, if exist all attributes (coincidence) or that class has no attributes, then simply copy
            #           those attributes in the new class

            # Create the class
            c = cls()

            # Check if exists all attributes (except internal variables),only if there are attributes
            if len(attrs) != 0:
                data_key_set = set(list(data))
                data_key_set.remove(AccessDatabase.ID_FIELD)
                data_key_set.remove(AccessDatabase.TIMESTAMP_FIELD)
                data_key_set.remove(AccessDatabase.DELETED_COUNT)
                data_key_set.remove(AccessDatabase.UPDATED_COUNT)
                intersect = attrs_set.intersection(data_key_set)
                attrs_eq = intersect == attrs_set

                if not attrs_eq:
                    raise DatabaseObjectException(ErrorMessages.DISTINCT_ATTRIBUTES_ERROR)

            # Copy values from data to instance
            for attr, value in data.items():
                setattr(c, attr, value)

            # Add to output
            output.append(c)

        # Return list of the objects
        return output

    def __repr__(self):
        return str(self.__dict__)


class DatabaseObjectException(InfraException):
    pass


class ErrorMessages:
    """
    Class of standar messages of the module
    """

    # Error messages
    CONNECTION_ERROR = 'Could not connect to datastore'
    GET_ERROR = 'Error getting data'
    PUT_ERROR = 'Error storing data'
    UPDATE_ERROR = 'Error updating data'
    REMOVE_ERROR = 'Error removing data'
    REMOVE_NON_EXISTENT_WARNING = 'Schema or subschema does not exist'
    CONFIGURATION_ERROR = 'Error configuring datastore'
    KEYFILE_ERROR = 'Not found the key'
    ID_ERROR = 'Error in the ID format'
    SCHEMA_ERROR = 'Error accessing non-existent schema'
    CRITERIA_ERROR = 'Error in action criteria'
    DATA_ERROR = 'Error in input data'
    REPR_ERROR = 'Method __repr__ must be implemented'
    INHERITANCE_ERROR = 'Data must inherit from DatabaseObject'
    DISTINCT_ATTRIBUTES_ERROR = 'Attributes not are the same'
    KO_ERROR = 'KO error'
    INDEX_VALUE_ERROR = 'Wrong value of id'
    GET_INDEX_ERROR = 'Error recovering index'
    UPDATE_INDEX_ERROR = 'Error updating index in datastore'
