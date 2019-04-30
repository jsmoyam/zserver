import Pyro4
from flask import Flask, request, jsonify
from flask_classful import FlaskView
from flask_httpauth import HTTPBasicAuth

from flask_socketio import SocketIO, Namespace, emit

from common import config
from common.app_config import AppConfig
from common.app_model import AppException, DataResultSchema, GenericErrorMessages
from common.infra_tools.decorators import apply_decorator_for_all_methods
from common.infra_modules.shell_manager_module.shell_module import MetaShellModule


logger = config.get_log(AppConfig.MAIN_CONFIGURATION)

# Instance flask app
rest_app = Flask(__name__)
socketio = SocketIO(rest_app)
auth = HTTPBasicAuth()



# Expose module from remote procedure call
rpc_app = None
rpc_ns = None
rpc_active = config.is_value_active(AppConfig.MAIN_CONFIGURATION, AppConfig.RPC_ACTIVE)
if rpc_active:
    try:
        exposed_host = config.get_value(AppConfig.MAIN_CONFIGURATION, AppConfig.EXPOSED_HOST)
        exposed_port = int(config.get_value(AppConfig.MAIN_CONFIGURATION, AppConfig.EXPOSED_PORT))
        rpc_client_ns_port = int(config.get_value(AppConfig.MAIN_CONFIGURATION, AppConfig.RPC_CLIENT_NS_PORT))
        rpc_app = Pyro4.Daemon(host=exposed_host, port=exposed_port)
        rpc_ns = Pyro4.locateNS(port=rpc_client_ns_port)
    except AppException:
        logger.info('No configuration found for rpc')


class ViewData:
    """
    Class that store data from view
    """
    def __init__(self, cls: type, route: str):
        self.cls = cls
        self.route = route


class MetaModule(type):
    def __new__(cls, name, bases, attrs):

        def auto_init(self, module_config: AppConfig, module_name: str):
            """
            Constructor for all modules
            :param self:
            :param module_config:
            :param module_name:
            :return:
            """
            self.module_config = module_config
            self.module_name = module_name
            logger.info('Initializing module {}'.format(module_name))
            self.initialize()
            logger.info('Initialized  module {}'.format(module_name))

        def create_output(self, cls_result, cls_schema, data: object, code, msg: str = '',
                          exception: Exception = None) -> str:
            """
            Create result object from data
            :param self:
            :param cls_result: result object from module
            :param cls_schema: data schema
            :param data: object data
            :param code: error code
            :param msg: message code
            :param exception: exception if exists
            :return: result object
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

            result = cls_result(code=code, data=data_result, msg=msg, exception=exception)
            response = jsonify(DataResultSchema().dumps(result))
            output = str(response.json[0])

            return output

        def create_input(self, cls_input_data, cls_input_data_schema) -> object:
            """
            This method create an object from POST request
            Has no sense using this method in GET/PUT/DELETE requests
            :param self:
            :param cls_input_data: class that represents object
            :param cls_input_data_schema: schema of the object
            :return: object filled with data from request
            """
            validate_input = cls_input_data_schema().load(request.json)

            if len(validate_input.errors) > 0:
                raise AppException(msg=GenericErrorMessages.VALIDATION_ERROR)

            return cls_input_data(**request.json)

        attrs['__init__'] = auto_init
        attrs['create_input'] = create_input
        attrs['create_output'] = create_output
        attrs['views'] = list()
        # attrs['shells'] = list()
        return super(MetaModule, cls).__new__(cls, name, bases, attrs)


class Module(metaclass=MetaModule):

    def register_url(self, cls, route: str):
        """
        Register module views
        :return: nothing
        """

        cls.app_module = self
        self.views.append(ViewData(cls, route))
        cls.register(rest_app, route_base=route)
        logger.info('Route added: {} - {}'.format(cls, route))


class ViewModule(FlaskView):
    pass


class ShellModule(metaclass=MetaShellModule):
    pass


def authenticate(except_private_internal=True):
    """ Apply authenticator decorator to all methods in a class view"""
    return apply_decorator_for_all_methods(auth.login_required, except_private_internal)


def stop_rest_app():
    """
    The shutdown functionality is written in a way that the server will finish handling the current request
    and then stop
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError(GenericErrorMessages.WERKZEUG_NOT_RUNNING)
    func()
