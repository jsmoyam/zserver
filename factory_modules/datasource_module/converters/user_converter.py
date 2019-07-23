from common import config
from common.infra_tools.hashes import hash_password
from factory_modules.datasource_module import MODULE_NAME
from factory_modules.datasource_module.base_datasource_module import User, Permission
from factory_modules.datasource_module.model_datasource_module import DatasourceException, DatasourceErrorCode
from factory_modules.datasource_module.models.user_model import UserInputData, UserRetrieveInputData, UserCreateInputData, \
    UserUpdateInputData, UserDeleteInputData, DsUserErrorCode

# Get the module logger
logger = config.get_log(MODULE_NAME)


def converter_user(database_module, user_input: UserInputData):
    try:

        # Creation action
        if isinstance(user_input, UserCreateInputData):

            logger.debug('Creating user with name {}'.format(user_input.username))

            # Get the user
            user_exist = database_module.db.read(User, username=user_input.username)

            if not user_exist:
                # Hash the password to store it
                hashed_password = hash_password(user_input.password)

                # Get the permissions list
                permissions_list = [database_module.db.read(Permission, id=p) for p in user_input.permissions]

                # Create the object to add
                user_to_add = User(username=user_input.username, password=hashed_password,
                                   permissions=permissions_list, is_active=1)

                return user_to_add
            else:
                # User with same name exist
                raise DatasourceException(DsUserErrorCode.DS_USER_EXIST_ERROR)

        # Retrieve action
        elif isinstance(user_input, UserRetrieveInputData):

            # Get keys to filter
            filters = {key: value for key, value in user_input.__dict__.items() if value}

            logger.debug('Retrieving users with filters {}'.format(str(filters)))

            # Add active filter to get only not deleted users
            filters.update({'is_active': 1})

            return (User,), filters

        # Update action
        elif isinstance(user_input, UserUpdateInputData):

            logger.debug('Updating user with id {}'.format(user_input.id))

            # Get the user
            user_update = database_module.db.read(User, id=user_input.id)

            if user_update:

                # Username changed
                if user_update.username != user_input.username:
                    # Check if new username exists
                    username_exist = database_module.db.read(User.username, username=user_input.username)

                    if username_exist:
                        # User with same name exist
                        raise DatasourceException(DsUserErrorCode.DS_USER_EXIST_ERROR)

                # Hash the new password to store it
                hashed_password = hash_password(user_input.password)

                # Get the permissions list
                permissions_list = [database_module.db.read(Permission, id=p) for p in user_input.permissions]

                # Set the new values to the user
                user_update.username = user_input.username
                user_update.password = hashed_password
                user_update.permissions = permissions_list
                user_update.is_active = user_input.is_active

                return user_update

            else:
                # User does not exist
                raise DatasourceException(DsUserErrorCode.DS_USER_NOT_FOUND_ERROR)

        # Delete action
        elif isinstance(user_input, UserDeleteInputData):

            logger.debug('Deleting user with id {}'.format(user_input.id))

            # Get the user to delete
            user_delete = database_module.db.read(User, id=user_input.id)

            if user_delete:

                # Set is_active to 0
                user_delete.is_active = 0

                return user_delete

            else:
                # User does not exist
                raise DatasourceException(DsUserErrorCode.DS_USER_NOT_FOUND_ERROR)

    except Exception as e:
        logger.error(DatasourceErrorCode.DATASOURCE_DB_ERROR_DES.formatter(e))

        output_error = e.error_code \
            if isinstance(e, DatasourceException) else DatasourceErrorCode.DATASOURCE_DB_ERROR
        raise DatasourceException(output_error)
