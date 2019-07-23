import logging

from common.app_model import AppHTTPStatus, AppException
from common.module import ViewModule, authenticate, handle_errors
from common.infra_tools.decorators import log_function
from factory_modules.datasource_module.datasource_module import MODULE_NAME
from factory_modules.datasource_module.model_datasource_module import DatasourceResult, DatasourceException
from factory_modules.datasource_module.models.user_model import DsUserMessage

# Get the module logger
logger = logging.getLogger(MODULE_NAME)


@authenticate()
@handle_errors((DatasourceException, AppException), DatasourceResult)
class UserModuleView(ViewModule):
    """
    Class that defines all the views from user's CRUD
    """

    @log_function(logger)
    def index(self):
        """
        HTTP get to retrieve all users

        :return: Schema with data result
        :rtype: DatasourceResult
        """
        from factory_modules.datasource_module.models.user_model import UserRetrieveInputData, UserRetrieveOutputSchema

        # Create object from input request
        user_data = UserRetrieveInputData(id=None)

        # Retrieve the users
        users = self.app_module.retrieve(user_data)

        # Convert object to output object
        result = self.app_module.create_output(DatasourceResult, UserRetrieveOutputSchema, AppHTTPStatus.OK, data=users,
                                               msg=DsUserMessage.DATASOURCE_USER_RETRIEVED)
        return result

    @log_function(logger)
    def get(self, id_user):
        """
        HTTP get to retrieve an user

        :return: Schema with data result
        :rtype: DatasourceResult
        """
        from factory_modules.datasource_module.models.user_model import UserRetrieveInputData, UserRetrieveOutputSchema

        # Create object from input request
        user_data = UserRetrieveInputData(id=id_user)

        # Retrieve the user
        user = self.app_module.retrieve(user_data)

        # Convert object to output object
        result = self.app_module.create_output(DatasourceResult, UserRetrieveOutputSchema, AppHTTPStatus.OK, data=user,
                                               msg=DsUserMessage.DATASOURCE_USER_RETRIEVED)
        return result

    @log_function(logger)
    def post(self):
        """
        HTTP post to create an user

        :return: Schema with data result
        :rtype: DatasourceResult
        """
        from factory_modules.datasource_module.models.user_model import UserCreateInputData, UserCreateInputSchema

        # Create object from input request
        user_data = self.app_module.create_input(UserCreateInputData, UserCreateInputSchema)

        # Create the user
        self.app_module.create(user_data)

        # Convert object to output object
        result = self.app_module.create_output(DatasourceResult, None, AppHTTPStatus.OK,
                                               msg=DsUserMessage.DATASOURCE_USER_CREATED)
        return result

    @log_function(logger)
    def put(self):
        """
        HTTP put to update an user

        :return: Schema with data result
        :rtype: DatasourceResult
        """
        from factory_modules.datasource_module.models.user_model import UserUpdateInputData, UserUpdateInputSchema

        # Create object from input request
        user_data = self.app_module.create_input(UserUpdateInputData, UserUpdateInputSchema)

        # Update the user
        self.app_module.update(user_data)

        # Convert object to output object
        result = self.app_module.create_output(DatasourceResult, None, AppHTTPStatus.OK,
                                               msg=DsUserMessage.DATASOURCE_USER_UPDATED)
        return result

    @log_function(logger)
    def delete(self, id_user):
        """
        HTTP delete to remove an user

        :return: Schema with data result
        :rtype: DatasourceResult
        """
        from factory_modules.datasource_module.models.user_model import UserDeleteInputData

        # Create object from input request
        user_data = UserDeleteInputData(id=id_user)

        # Retrieve the user
        self.app_module.delete(user_data)

        # Convert object to output object
        result = self.app_module.create_output(DatasourceResult, None, AppHTTPStatus.OK,
                                               msg=DsUserMessage.DATASOURCE_USER_DELETED)
        return result
