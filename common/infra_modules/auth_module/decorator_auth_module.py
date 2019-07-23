import functools

import common

from common.infra_modules.auth_module.model_auth_module import AuthErrorCode, AuthException
from common.infra_tools.errors_output import create_output_on_error


class AuthenticationRequired:
    """
    Decorator that control the access to the views with authentication.
    It'll use auth module.
    """

    def __init__(self, auth):
        """
        Constructor: Create the permissions decorator

        :param auth: api authenticate
        """

        self.auth = auth

    def __call__(self, func):
        """
        Create a wrap function to control the permissions of the user

        :param func: wrapper function
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            High-order function that act the main function

            :param args: the leftmost positional arguments
            :param kwargs: the keyword arguments
            """

            # Get the token
            user_or_token = self.auth.username()

            # Get the auth_module
            auth_module = common.module_manager.get_module('auth_module')

            try:
                # Check permissions
                is_logged = auth_module.check_token(user_or_token)

                if is_logged:
                    # Execute the function
                    f_result = func(*args, **kwargs)

                    return f_result
                else:
                    raise AuthException(AuthErrorCode.AUTH_USER_DOES_NOT_PERMISSION)

            except AuthException as ae:
                return create_output_on_error(ae.error_code)

        return wrapper


class PermissionsRequired:
    """
    Decorator that control the access to the views with permissions.
    Need to be logged in the system. Add @authenticate in the view.
    It'll use auth module.
    """

    def __init__(self, auth, permissions_required: list):
        """
        Constructor: Create the permissions decorator

        :param auth: api authenticate
        :param permissions_required: list of permissions to control
        """

        self.auth = auth
        self.permissions_required = permissions_required

    def __call__(self, func):
        """
        Create a wrap function to control the permissions of the user

        :param func: wrapper function
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """
            High-order function that act the main function

            :param args: the leftmost positional arguments
            :param kwargs: the keyword arguments
            """

            # Get the token
            token = self.auth.username()

            if token:
                # Get the auth_module
                auth_module = common.module_manager.get_module('auth_module')

                # Check permissions
                has_permission = auth_module.check_user_permissions(token, self.permissions_required)

                if has_permission:
                    # Execute the function
                    f_result = func(*args, **kwargs)

                    return f_result

            # Return error message
            return create_output_on_error(AuthErrorCode.AUTH_USER_DOES_NOT_PERMISSION)

        return wrapper
