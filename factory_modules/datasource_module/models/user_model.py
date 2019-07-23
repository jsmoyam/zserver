from marshmallow import Schema, fields

from common.app_model import AppHTTPStatus, ErrorCode, AppMessage


# region Models

class UserInputData:
    """
    Class that defines the user input data from api request
    """

    entity_name = 'user'

    def __init__(self, id: int, username: str = '', password: str = '',
                 permissions: list = None, is_active: int = None):
        """
        Constructor: Init variables from request

        :param id: user's id
        :param username: user's username
        :param password: user's password
        :param permissions: user's permissions ids
        :param is_active: user's status
        """

        self.id = id
        self.username = username
        self.password = password
        self.permissions = permissions
        self.is_active = is_active


class UserRetrieveInputData(UserInputData):
    """
    Class that defines the create user input data from api request
    """

    def __init__(self, id: int):
        """
        Constructor: Init variables from request

        :param id: user's id
        """

        super().__init__(id)


class UserCreateInputData(UserInputData):
    """
    Class that defines the create user input data from api request
    """

    def __init__(self, username: str, password: str, permissions: list):
        """
        Constructor: Init variables from request

        :param username: user's username
        :param password: user's password
        :param permissions: user's permissions ids
        """

        super().__init__(None, username, password, permissions)


class UserUpdateInputData(UserInputData):
    """
    Class that defines the update user input data from api request
    """

    def __init__(self, id: int, username: str, new_password: str, permissions: list,
                 is_active: int):
        """
        Constructor: Init variables from request

        :param id: user's id
        :param username: user's username
        :param new_password: new user's password
        :param permissions: user's permissions ids
        :param is_active: user's status
        """

        super().__init__(id, username, new_password, permissions, is_active)


class UserDeleteInputData(UserInputData):
    """
    Class that defines the delete user input data from api request
    """

    def __init__(self, id: int):
        """
        Constructor: Init variables from request

        :param id: user's id
        """

        super().__init__(id)

# endregion


# region Schemas

class UserPermissionRetrieveOutputSchema(Schema):
    """
    Output permissions retrieved user
    """

    id = fields.Int()
    name = fields.Str()


class UserRetrieveOutputSchema(Schema):
    """
    Output retrieved user
    """

    id = fields.Int()
    username = fields.Str()
    password = fields.Str()
    permissions = fields.List(fields.Nested(UserPermissionRetrieveOutputSchema))
    is_active = fields.Int()


class UserCreateInputSchema(Schema):
    """
    Input user to create
    """

    username = fields.Str()
    password = fields.Str()
    permissions = fields.List(fields.Int())


class UserUpdateInputSchema(Schema):
    """
    Input user to update
    """

    id = fields.Int()
    username = fields.Str(required=False)
    new_password = fields.Str(required=False)
    permissions = fields.List(fields.Int(required=False))
    is_active = fields.Int(required=False)

# endregion


# region Messages

class DsUserMessage(AppMessage):
    """
    Datasource user module messages
    """

    DATASOURCE_USER_CREATED = 'User created successfully'
    DATASOURCE_USER_RETRIEVED = 'User retrieved successfully'
    DATASOURCE_USER_UPDATED = 'User updated successfully'
    DATASOURCE_USER_DELETED = 'User deleted successfully'

# endregion


# region ErrorCodes

class DsUserErrorCode(ErrorCode):
    """
    Datasource user module error codes. Codes from 50 to 59.
    """

    DS_USER_EXIST_ERROR = 50, 'USER_EXIST', 'An user exist with the same name', AppHTTPStatus.BAD_REQUEST
    DS_USER_NOT_FOUND_ERROR = 51, 'USER_NOT_FOUND', 'The input user does not exist', AppHTTPStatus.NOT_FOUND

# endregion
