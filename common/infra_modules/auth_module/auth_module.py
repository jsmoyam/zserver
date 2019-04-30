from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

import common
from common import config
from common.app_model import GenericErrorMessages, AppException

from common.infra_modules.infra_module import InfraModule
from common.infra_tools.decorators import log_function

from common.infra_modules.auth_module import MODULE_NAME
from common.infra_modules.auth_module.views_auth_module import LoginModuleView

logger = config.get_log(MODULE_NAME)


class AuthModule(InfraModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """

        # Token expiration 10 minutes
        self.token_expiration = 3600*10
        self.secret_key = self.module_config.get_value(MODULE_NAME, 'secret_key')
        self.tokens = dict()

        # Datasource module
        #self.ds = common.module.get_module('datasource_module')

        self.register_url(LoginModuleView, '/auth/login')

    @log_function(logger)
    def login(self, username: str, password: str) -> str:
        """ This methods do login and return token """

        # Check if username and password are in database
        #user_id = self.ds.get_user_id(username, password)
        user_id = 1

        # If user exists, generate token, store token and return it. Else raise exception
        if user_id:
            token = self.generate_token(user_id)
            self.tokens[token] = user_id
            logger.info('{} username: {} user_id: {}'.format(GenericErrorMessages.USER_LOGIN, username, user_id))
            return token
        else:
            raise AppException(logger=logger, msg='{} username: {}'.format(GenericErrorMessages.USER_NOT_FOUND, username))

    @log_function(logger)
    def logout(self, token: str):
        """ This method do logout """

        # Recover payload (user_id) from token
        logger.debug('Recover user_id from token')
        user_id = self.get_user_id_from_token(token)

        # Remove token from dictionary. If raise exception then token does not exist
        try:
            self.tokens.pop(token)
        except KeyError:
            # Something went wrong because token does not exist
            logger.error('{} user_id: {}'.format(GenericErrorMessages.TOKEN_DOES_NOT_EXIST_ERROR, user_id))
            raise AppException(msg=GenericErrorMessages.TOKEN_DOES_NOT_EXIST_ERROR)

    def generate_token(self, user_id: int):
        # Create token with user_id and secret_key
        s = Serializer(self.secret_key, expires_in=self.token_expiration)
        token_bytes = s.dumps({'id': user_id})
        token = token_bytes.decode('utf-8')
        return token

    def get_user_id_from_token(self, token: str) -> int:
        # Recover user_id from token
        try:
            s = Serializer(self.secret_key)
            payload = s.loads(token)
            return payload
        except SignatureExpired:
            logger.info(GenericErrorMessages.EXPIRED_TOKEN_ERROR)
            raise AppException(msg=GenericErrorMessages.EXPIRED_TOKEN_ERROR)
        except BadSignature:
            logger.warning(GenericErrorMessages.BAD_SIGNATURE_TOKEN_ERROR)
            raise AppException(msg=GenericErrorMessages.BAD_SIGNATURE_TOKEN_ERROR)

    @log_function(logger)
    def check_token(self, token: str) -> bool:
        # Check if token is ok and it is in tokens dictionary
        self.get_user_id_from_token(token)

        if token in self.tokens:
            return True
        else:
            raise AppException(msg=GenericErrorMessages.TOKEN_DOES_NOT_EXIST_ERROR)
