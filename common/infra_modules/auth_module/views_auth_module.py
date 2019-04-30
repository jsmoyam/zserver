import logging

from common.module import ViewModule
from common.infra_tools.decorators import log_function

from common.infra_modules.auth_module import MODULE_NAME
from common.infra_modules.auth_module.model_auth_module import LoginInputData, LoginInputDataSchema, AAAResult

logger = logging.getLogger(MODULE_NAME)


# @authenticate()
class LoginModuleView(ViewModule):

    @log_function(logger)
    def post(self):
        # curl -d '{"username":"pepito", "password":"pepito123"}' -H "Content-type: application/json" -X POST http://localhost:5000/auth/login/

        # Create object from request
        login_data = self.app_module.create_input(LoginInputData, LoginInputDataSchema)

        # Process data to generate processed object
        token = self.app_module.login(login_data.username, login_data.password)

        # Convert output object to result object
        result = self.app_module.create_output(AAAResult, None, token, 'CODE_OK')
        return result
