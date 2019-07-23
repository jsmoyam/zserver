import common

from common import config
from common.infra_tools.hashes import check_password_hashed
from factory_modules.factory_module import FactoryModule
from factory_modules.datasource_module import MODULE_NAME
from factory_modules.datasource_module.base_datasource_module import Base, User
from factory_modules.datasource_module.model_datasource_module import DatasourceErrorCode, DatasourceException
from factory_modules.datasource_module.models.user_model import UserInputData
from factory_modules.datasource_module.views.user_view import UserModuleView

# Get the module logger
logger = config.get_log(MODULE_NAME)


class DatasourceModule(FactoryModule):
    """
    Module that get data from database
    """

    db_module: object

    def initialize(self):
        """
        This method create and initialize all variables and resources that are needed

        :return: None
        """

        try:
            # Get the database module
            self.db_module = common.module_manager.get_module('database_module')

            # Get the engine and session of database
            engine, session = self.db_module.db.get_connection()
            Base.metadata.create_all(engine)

            # Register the views of the module
            self.register_url(UserModuleView, '/user')

        except Exception as e:
            logger.error(DatasourceErrorCode.DATASOURCE_DB_ERROR_DES.formatter(e))
            raise DatasourceException(DatasourceErrorCode.DATASOURCE_DB_ERROR)

    def create(self, obj: object) -> object:
        """
        Read the object input data and create the entity
        :param obj: InputData

        :return: the entity
        :rtype: object
        """

        result = self.db_module.insert_from_obj(obj)

        if result:
            return result
        else:
            raise DatasourceException(
                DatasourceErrorCode.DATASOURCE_ENTITY_CREATE_ERROR.formatter(obj.__class__.__bases__[0].entity_name))

    def retrieve(self, obj: object) -> object:
        """
        Read the object input data and read the entity
        :param obj: InputData

        :return: the entity
        :rtype: object
        """

        result = self.db_module.read_from_obj(obj)

        if result:
            return result
        else:
            raise DatasourceException(
                DatasourceErrorCode.DATASOURCE_ENTITY_NOT_FOUND.formatter(obj.__class__.__bases__[0].entity_name))

    def update(self, obj: object) -> object:
        """
        Read the object input data and update the entity
        :param obj: InputData

        :return: the entity
        :rtype: object
        """

        result = self.db_module.update_from_obj(obj)

        if result:
            return result
        else:
            raise DatasourceException(
                DatasourceErrorCode.DATASOURCE_ENTITY_UPDATE_ERROR.formatter(obj.__class__.__bases__[0].entity_name))

    def delete(self, obj: object) -> object:
        """
        Read the object input data and delete the entity
        :param obj: InputData

        :return: the entity
        :rtype: object
        """

        # This list of entities do not delete, do update to active=0
        if isinstance(obj, UserInputData):
            result = self.db_module.update_from_obj(obj)
        else:
            result = self.db_module.delete_from_obj(obj)

        if result:
            return result
        else:
            raise DatasourceException(
                DatasourceErrorCode.DATASOURCE_ENTITY_DELETE_ERROR.formatter(obj.__class__.__bases__[0].entity_name))

    def get_user_id(self, name, password) -> int:
        """
        Retrieves user with given name and password (None if it doesn't exist)

        :param name: user's name
        :param password: user's hashed password

        :return: user's id
        :rtype: int
        """

        try:
            logger.debug('Getting user for name {}'.format(name))

            # Get the user
            user = self.db_module.db.read(User, username=name)

            if user:
                # Compare the input password with stored password
                pass_match = check_password_hashed(password, user.password)

                if pass_match:
                    logger.debug('User\'s password match'.format(name))
                    return user.id

                logger.debug('User\'s password do not match'.format(name))

            return None

        except Exception as e:
            logger.error(DatasourceErrorCode.DATASOURCE_DB_ERROR_DES.formatter(e))
            return None

    def get_user_permissions(self, user_id) -> list:
        """
        Retrieves user permissions with given user id (None if user doesn't exist)

        :param user_id: user's id

        :return: user's permissions
        :rtype: list
        """

        try:
            logger.debug('Getting user_permissions for user {}'.format(user_id))

            # Get the user permissions
            user = self.db.read(User, id=user_id)
            user_permissions = user.permissions

            return user_permissions

        except Exception as e:
            logger.error(DatasourceErrorCode.DATASOURCE_DB_ERROR_DES.formatter(e))
            return None

    # endregion
