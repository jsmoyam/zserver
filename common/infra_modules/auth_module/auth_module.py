from jwt import encode, decode, InvalidSignatureError, ExpiredSignatureError, DecodeError
from datetime import datetime, timedelta

import common

from common import config
from common.infra_modules.infra_module import InfraModule
from common.infra_modules.auth_module import MODULE_NAME
from common.infra_modules.auth_module.model_auth_module import AuthErrorCode, AuthException
from common.infra_modules.auth_module.views_auth_module import LoginModuleView, LogoutModuleView
from common.infra_tools.decorators import log_function

# Get the module logger
logger = config.get_log(MODULE_NAME)


# noinspection PyTypeChecker,PyUnresolvedReferences
class AuthModule(InfraModule):
    """
    Module that authenticate user to grant access to the app
    """

    token_expiration: int
    secret_key: str
    tokens: dict
    ds: InfraModule

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        """

        # Token expiration
        self.token_expiration = eval(self.module_config.get_value(MODULE_NAME, 'token_expiration'))
        self.secret_key = self.module_config.get_value(MODULE_NAME, 'secret_key')
        self.tokens = dict()

        # Get the Datasource module
        self.ds = common.module_manager.get_module('datasource_module')

        # Register the views of the module
        self.register_url(LoginModuleView, '/auth/login')
        self.register_url(LogoutModuleView, '/auth/logout')

    @log_function(logger)
    def login(self, username: str, password: str) -> str:
        """
        This method do login and return token if user exist

        :param username: username
        :param password: password

        :return: token
        :rtype: str
        """

        logger.debug('User {} is trying to login'.format(username))

        # Check if username and password are in database
        user_id = self.ds.get_user_id(username, password)

        if user_id:

            logger.debug('Generating token for user {}'.format(username))

            # Generate token and store it
            token = self.__generate_token__(user_id)
            self.tokens[token] = user_id
            return token
        else:
            logger.error(AuthErrorCode.AUTH_USER_NOT_FOUND.formatter(username))
            raise AuthException(AuthErrorCode.AUTH_USER_NOT_FOUND.formatter(username))

    @log_function(logger)
    def logout(self, token: str):
        """
        This method do logout and return token if user exist

        :param token: user's token
        """

        logger.debug('An user is trying to logout')

        # Recover payload (user_id) from token
        user = self.get_user_id_from_token(token)

        if user:
            logger.debug('User with id {} logout'.format(user['id']))
            # Remove token from dictionary. If raise exception then token does not exist
            self.tokens.pop(token)
        else:
            logger.error(AuthErrorCode.AUTH_TOKEN_DOES_NOT_EXIST)
            raise AuthException(AuthErrorCode.AUTH_TOKEN_DOES_NOT_EXIST)

    def __generate_token__(self, user_id: int) -> str:
        """
        Create a new token with user_id and expiration date

        :param user_id: user's id

        :return: token
        :rtype: str
        """

        # Calculate the date expiration of the token
        exp_date = datetime.utcnow() + timedelta(0, self.token_expiration)
        # Generate the token
        token_bytes = encode({'id': user_id, 'exp': exp_date}, self.secret_key, algorithm='HS256')
        token = token_bytes.decode('utf-8')

        return token

    def get_user_id_from_token(self, token: str) -> dict:
        """
        Get the user_id from token passed by parameter

        :param token: a token

        :return: user_id
        :rtype: int
        """

        try:
            payload = decode(token, self.secret_key, algorithms='HS256')
            return payload
        except ExpiredSignatureError:
            logger.info(AuthErrorCode.AUTH_TOKEN_EXPIRED)
            raise AuthException(AuthErrorCode.AUTH_TOKEN_EXPIRED)
        except (InvalidSignatureError, DecodeError):
            logger.info(AuthErrorCode.DecodeError)
            raise AuthException(AuthErrorCode.DecodeError)

    @log_function(logger)
    def check_token(self, token: str) -> bool:
        """
        Check if token exists
        :param token: user's token

        :return: True if token exists
        :rtype: bool
        """

        logger.debug('Checking valid token')

        # Check if token is ok and it is in tokens dictionary
        user = self.get_user_id_from_token(token)

        if user and token in self.tokens:
            return True
        else:
            return False

    @log_function(logger)
    def check_user_permissions(self, token: str, permissions_list: list) -> bool:
        """
        This method do check if user has a permission passed by parameter

        :param token: user's token
        :param permissions_list: list of permissions to control

        :return: True if user has permission
        :rtype: bool
        """

        logger.debug('Checking permissions {} for user'.format(permissions_list))

        # Get the user_id from token
        user = self.get_user_id_from_token(token)

        if user and token in self.tokens:
            # Get user permissions
            user_permissions = self.ds.get_user_permissions(user['id'])

            if user_permissions:
                # Check if user has a required permission
                for up in user_permissions:
                    if up in permissions_list:
                        logger.debug('User {} has permission'.format(user['id']))
                        return True
            else:
                logger.info(AuthErrorCode.AUTH_USER_PERMISSIONS_NOT_FOUND.formatter(username))
        else:
            logger.info(AuthErrorCode.AUTH_TOKEN_DOES_NOT_EXIST)

        return False
