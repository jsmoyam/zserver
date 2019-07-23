import logging

from common.app_model import AppHTTPStatus, AppException
from common.module import ViewModule, authenticate, handle_errors
from common.infra_modules.auth_module import MODULE_NAME
from common.infra_modules.auth_module.model_auth_module import LoginInputData, LogoutInputData, LoginInputDataSchema, \
    LogoutInputDataSchema, AuthResult, AuthMessage, AuthException
from common.infra_tools.decorators import log_function

# Get the module logger
logger = logging.getLogger(MODULE_NAME)


@handle_errors((AuthException, AppException), AuthResult)
class LoginModuleView(ViewModule):
    """
    Class that defines all the views from login
    """

    @log_function(logger)
    def post(self):
        """
        HTTP post to do login

        :return: Schema with data result
        :rtype: AuthResult
        """

        # Create object from input request
        login_data = self.app_module.create_input(LoginInputData, LoginInputDataSchema)

        # Do login and get the token
        token = self.app_module.login(login_data.username, login_data.password)

        # Convert object to output object
        result = self.app_module.create_output(AuthResult, None, AppHTTPStatus.OK, token,
                                               msg=AuthMessage.AUTH_USER_LOGIN)
        return result


@authenticate()
@handle_errors((AuthException, AppException), AuthResult)
class LogoutModuleView(ViewModule):
    """
    Class that defines all the views from logout
    """

    @log_function(logger)
    def post(self):
        """
        HTTP post to do logout

        :return: Schema with data result
        :rtype: AuthResult
        """

        # Create object from input request
        login_data = self.app_module.create_input(LogoutInputData, LogoutInputDataSchema)

        # Try to do logout
        self.app_module.logout(login_data.token)

        # Convert object to output object
        return self.app_module.create_output(AuthResult, None, AppHTTPStatus.OK, msg=AuthMessage.AUTH_USER_LOGOUT)
