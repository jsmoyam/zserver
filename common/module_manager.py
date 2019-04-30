import logging
import Pyro4
import copy
import importlib

from common import config
from common.app_config import AppConfig
from common.app_model import AppException, GenericErrorMessages
from common.module import Module, rest_app, socketio, rpc_app, rpc_ns, auth
from common.infra_modules.module_summary import get_infra_modules

logger = config.get_log(AppConfig.MAIN_CONFIGURATION)

# Dict that store all modules
modules_manager = dict()


def add_module(module_config: AppConfig, module_name: str) -> None:
    """
    Create a module instance and store it
    :param module_config: config for module
    :param module_name:  module name
    :return: None
    """
    module = module_names[module_name](module_config, module_name)
    modules_manager[module_name] = module


def add_remote_module(module_name: str, connect_exposed_module: str) -> None:
    """
    Create a remote module instance and store it
    :param module_name:  module name
    :param connect_exposed_module: module to connect
    :return: None
    """

    module = Pyro4.Proxy('PYRONAME:{}'.format(connect_exposed_module))
    modules_manager[module_name] = module


def get_module(module_name: str) -> Module:
    """
    Get module by name
    :param module_name: str
    :return: module
    """
    if module_name not in modules_manager.keys():
        raise AppException(msg=GenericErrorMessages.MODULE_NOT_FOUND)
    return modules_manager[module_name]


def get_all_modules(except_shell_manager_module=False) -> dict:
    """
    Get all modules
    :param except_shell_module: delete shell module from the list
    :return: dict of modules
    """
    if not except_shell_manager_module:
        return modules_manager
    else:
        modules_manager_tmp =copy.copy(modules_manager)
        del modules_manager_tmp['shell_manager_module']
        return modules_manager_tmp


def expose_module(module_name: str, exposed_name: str):
    module = get_module(module_name)
    module.exposed = True
    Pyro4.expose(module.__class__)
    uri = rpc_app.register(module)
    rpc_ns.register(exposed_name, uri)


def start_api():
    logger_flask = logging.getLogger('werkzeug')
    for hdlr in logger_flask.handlers[:]:  # remove all old handlers
        logger_flask.removeHandler(hdlr)


    config.setup_logger(logger_flask, config.get_value(AppConfig.API_CONFIGURATION, AppConfig.ATTR_LOG_LEVEL),
                        AppConfig.API_CONFIGURATION)
    config.setup_logger(rest_app.logger, config.get_value(AppConfig.API_CONFIGURATION, AppConfig.ATTR_LOG_LEVEL),
                        AppConfig.API_CONFIGURATION)
    host = config.get_value(AppConfig.API_CONFIGURATION, AppConfig.API_HOST)
    port = config.get_value(AppConfig.API_CONFIGURATION, AppConfig.API_PORT)
    debug = config.is_value_active(AppConfig.API_CONFIGURATION, AppConfig.API_DEBUG)
    ssl = 'adhoc' if config.is_value_active(AppConfig.API_CONFIGURATION, AppConfig.API_SSL) else None
    logger.info('REST API starting')

    socketio.run(rest_app)
    # socketio.run(rest_app, host=host, port=port, debug=debug, use_reloader=False, threaded=True, ssl_context=ssl)
    # rest_app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True, ssl_context=ssl)





def start_rpc():
    logger.info('RPC starting')
    rpc_app.requestLoop()


@auth.verify_password
def verify_password(username_or_token, password):
    """
    This function check authentication for flask . It will use auth module
    This function is automatically called when executed api function
    """

    # Get module object from rpc and execute check_token method
    try:
        auth = get_module('auth_module')
        return auth.check_token(username_or_token)
    except AppException:
        return False


# Create dictionary with all modules: infrastructure and product modules

infra_modules = get_infra_modules()

# Get product summary module class as string from configuration and then import dynamically
# It uncouples product modules from the original code
product_summary_file = config.get_value(AppConfig.MAIN_CONFIGURATION, AppConfig.APP_PRODUCT_SUMMARY_FILE)
product_module_summary = importlib.import_module(product_summary_file)
product_modules = product_module_summary.get_product_modules()

# Join two dictionaries
module_names = {**infra_modules, **product_modules}

