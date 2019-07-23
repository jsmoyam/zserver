import logging
import Pyro4

from flask import Flask, request, jsonify
from flask_classful import FlaskView
from flask_httpauth import HTTPBasicAuth
from flask_socketio import SocketIO

from common import config
from common.app_config import AppConfig
from common.app_model import AppHTTPStatus, AppDataResultSchema, AppException, AppErrorCode
from common.infra_modules.auth_module.decorator_auth_module import AuthenticationRequired, PermissionsRequired
from common.infra_modules.shell_manager_module.shell_module import MetaShellModule
from common.infra_tools.decorators import apply_decorator_for_all_methods, error_handler_views, \
    apply_decorator_to_a_method
from common.infra_tools.pyrons_server import PyroNameServer

# Get the app logger
logger = config.get_log(AppConfig.APP_MAIN_CONFIGURATION)

# Instance flask app
rest_app = Flask(__name__)
socket_io = SocketIO(rest_app)
auth = HTTPBasicAuth()

# Expose module from remote procedure call
rpc_daemon = None
rpc_ns_server = None
rpc_ns_proxy = None
rpc_active = config.is_value_active(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.RPC_ACTIVE)
if rpc_active:
    try:
        # Get rpc host and rpc port configuration
        exposed_host = config.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.RPC_EXPOSED_HOST)
        exposed_port = int(config.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.RPC_EXPOSED_PORT))

        # Instance pyro4 name server
        rpc_ns_server = PyroNameServer()
        rpc_ns_server.start()

        # Start rpc daemon app with pyro4
        rpc_daemon = Pyro4.Daemon(host=exposed_host, port=exposed_port)

        # Get the pyro4 proxy for a name server
        rpc_ns_proxy = Pyro4.locateNS()

    except AppException:
        logger.error('No configuration found for RPC')


class ViewData:
    """
    Class that store data from view
    """

    def __init__(self, cls: type, route: str):
        """
        Constructor: Instance view data

        :param cls: instance of the module
        :param route: route to add the view
        """

        self.cls = cls
        self.route = route


class MetaModule(type):
    """
    Metaclass to use for all modules
    """

    def __new__(msc, name, bases, attrs):

        def auto_init(self, module_config: AppConfig, module_name: str):
            """
            Define the constructor for all modules

            :param self: Refers to the object method
            :param module_config: Module's configuration
            :param module_name: Module's name
            """

            self.module_config = module_config
            self.module_name = module_name
            logger.info('Initializing module {}'.format(module_name))
            self.initialize()
            logger.info('Initialized  module {}'.format(module_name))

        def create_output(self, cls_result, cls_schema, status_code: AppHTTPStatus, data: object = None,
                          msg: str = '', error: Exception = None) -> str:
            """
            Create result object from data

            :param self: class attribute
            :param cls_result: result object from module
            :param cls_schema: data schema
            :param status_code: http status code
            :param data: object data
            :param msg: message code
            :param error: exception if exists

            :return: result object
            :rtype: str
            """

            list_mode = False
            if isinstance(data, list):
                list_mode = True

            # If there is no schema for object then it is a basic type
            if cls_schema is None:
                data_result = data
            else:
                data_json = jsonify(cls_schema(many=list_mode).dump(data)[0])
                data_result = data_json.json

            # If there an error, success false
            success = error is None
            result = cls_result(success=success, status_code=status_code.value, data=data_result, msg=msg,
                                error=error)
            response = jsonify(AppDataResultSchema().dumps(result))
            output = str(response.json[0])

            return output

        def create_input(self, cls_input_data, cls_input_data_schema) -> object:
            """
            This method create an object from POST request
            Has no sense using this method in GET/PUT/DELETE requests

            :param self: class attribute
            :param cls_input_data: class that represents object
            :param cls_input_data_schema: schema of the object

            :return: object filled with data from request
            """

            try:
                validate_input = cls_input_data_schema().load(request.json)

                if len(validate_input.errors) > 0:
                    raise AppException(AppErrorCode.APP_BAD_REQUEST_ERROR, logger, logging.ERROR)

                return cls_input_data(**request.json)
            except TypeError as te:
                raise AppException(AppErrorCode.APP_BAD_REQUEST_ERROR, logger, logging.ERROR)

        attrs['__init__'] = auto_init
        attrs['create_input'] = create_input
        attrs['create_output'] = create_output
        attrs['views'] = list()
        # attrs['shells'] = list()
        return super(MetaModule, msc).__new__(msc, name, bases, attrs)


class Module(metaclass=MetaModule):
    """
    Metaclass that define the base of all modules
    """

    def __init__(self):
        self.views = None

    def register_url(self, cls, route: str):
        """
        Register the views of the modules

        :param cls: instance of the module
        :param route: route to add the view
        """

        cls.app_module = self
        self.views.append(ViewData(cls, route))
        cls.register(rest_app, route_base=route)
        logger.info('Route added: {} - {}'.format(cls, route))


class ViewModule(FlaskView):
    """
    Class to implement views from the modules'views
    """

    pass


class ShellModule(metaclass=MetaShellModule):
    """
    Class to implement shell module from the modules
    """
    pass


def authenticate(except_private_internal=True):
    """
    Function to apply authenticator decorator to all methods in a class

    :param except_private_internal:
    """

    return apply_decorator_for_all_methods(AuthenticationRequired(auth), except_private_internal)


def stop_rest_app():
    """
    The shutdown functionality is written in a way that the server will finish handling the current request
    and then stop
    """

    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError(AppErrorCode.APP_STOP_API_ERROR)
    func()


def handle_errors(exceptions: tuple = (AppException,), cls_result=AppDataResultSchema):
    """
    Function to apply error handler decorator to all methods in a class

    :param exceptions: tuple of exceptions to handle
    :param cls_result: schema to create output
    """

    return apply_decorator_for_all_methods(error_handler_views(exceptions, cls_result))


def permissions_required(permissions_list):
    """
    Function to apply permissions decorator to all methods in a class

    :param permissions_list: list of permissions to control
    """

    return apply_decorator_for_all_methods(PermissionsRequired(auth, permissions_list))


def permissions_required_method(permissions_list):
    """
    Function to apply permissions decorator to all methods in a class

    :param permissions_list: list of permissions to control
    """

    return apply_decorator_to_a_method(PermissionsRequired(auth, permissions_list))
