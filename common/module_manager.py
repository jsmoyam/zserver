import logging
import Pyro4
import copy
import importlib

from common import config
from common.app_config import AppConfig
from common.app_model import AppException, AppErrorCode
from common.module import Module, rest_app, rpc_daemon, rpc_ns_proxy, auth, socket_io
from common.infra_modules.module_summary import get_infra_modules
from common.infra_tools.errors_output import create_output_on_error

# Get the app logger
logger = config.get_log(AppConfig.APP_MAIN_CONFIGURATION)

# Dict that contains all the modules loaded
modules_manager = dict()


def add_module(module_config: AppConfig, module_name: str):
    """
    Create module instance and store it in the dict

    :param module_config: module configuration
    :param module_name: module name
    """

    module = module_names[module_name](module_config, module_name)
    modules_manager[module_name] = module


def add_remote_module(module_name: str, connect_exposed_module: str):
    """
    Create a remote module instance and store it in the dict

    :param module_name: module name
    :param connect_exposed_module: module to connect
    """

    module = Pyro4.Proxy('PYRONAME:{}'.format(connect_exposed_module))
    modules_manager[module_name] = module


def get_module(module_name: str) -> Module:
    """
    Get module by name passed as parameter

    :param module_name: name of the module

    :return: module found
    :rtype: Module
    """

    if module_name not in modules_manager.keys():
        logger.error(AppErrorCode.APP_MODULE_NOT_FOUND.formatter(module_name))
        raise AppException(AppErrorCode.APP_MODULE_NOT_FOUND)
    return modules_manager[module_name]


def get_all_modules(except_shell_manager_module=False) -> dict:
    """
    Get all modules

    :param except_shell_manager_module: delete shell module from the list

    :return: dict of modules
    """

    if not except_shell_manager_module:
        return modules_manager
    else:
        modules_manager_tmp = copy.copy(modules_manager)
        del modules_manager_tmp['shell_manager_module']
        return modules_manager_tmp


def expose_module(module_name: str, exposed_name: str):
    """
    Expose module via remote procedure call

    :param module_name: name to expose
    :param exposed_name: exposed name of the module
    """

    module = get_module(module_name)
    module.exposed = True
    Pyro4.expose(module.__class__)
    uri = rpc_daemon.register(module)
    rpc_ns_proxy.register(exposed_name, uri)


def start_api():
    """
    Set the configuration for flask API and start it
    """

    logger_flask = logging.getLogger('werkzeug')

    # Remove all handlers from the werkzeug logger
    for handler in logger_flask.handlers[:]:
        logger_flask.removeHandler(handler)

    # Setup flask logger
    config.setup_logger(logger_flask, config.get_value(AppConfig.API_CONFIGURATION, AppConfig.LOG_LEVEL),
                        AppConfig.API_CONFIGURATION)
    # Setup rest app logger
    config.setup_logger(rest_app.logger, config.get_value(AppConfig.API_CONFIGURATION, AppConfig.LOG_LEVEL),
                        AppConfig.API_CONFIGURATION)
    # Get the configuration
    host = config.get_value(AppConfig.API_CONFIGURATION, AppConfig.API_HOST)
    port = config.get_value(AppConfig.API_CONFIGURATION, AppConfig.API_PORT)
    debug = config.is_value_active(AppConfig.API_CONFIGURATION, AppConfig.API_DEBUG)
    ssl = None

    try:
        ssl_enabled = config.is_value_active(AppConfig.API_CONFIGURATION, AppConfig.API_SSL)

        if ssl_enabled:
            # Get the certificate and private key files
            priv_key_file = config.get_value(AppConfig.API_CONFIGURATION, AppConfig.API_SSL_PRIVATE_KEY)
            cert_file = config.get_value(AppConfig.API_CONFIGURATION, AppConfig.API_SSL_CERT)
    except AppException:
        ssl_enabled = False
        logger.error(AppErrorCode.APP_CONF_SSL_ERROR)

    # If ssl is enabled
    if ssl_enabled:
        from OpenSSL import SSL

        try:
            # Create the context ssl
            context = SSL.Context(SSL.TLSv1_2_METHOD)

            context.use_privatekey_file(priv_key_file)

            context.use_certificate_file(cert_file)
        except SSL.Error:
            logger.error(AppErrorCode.APP_SSL_ERROR)

    # Declare all the error handlers for some HTTP errors
    @rest_app.errorhandler(400)
    def bad_request(_error):
        return create_output_on_error(AppErrorCode.APP_BAD_REQUEST_ERROR)

    @rest_app.errorhandler(401)
    def unauthorized(_error):
        return create_output_on_error(AppErrorCode.APP_UNAUTHORIZED_ERROR)

    @rest_app.errorhandler(403)
    def forbidden(_error):
        return create_output_on_error(AppErrorCode.APP_FORBIDDEN_ERROR)

    @rest_app.errorhandler(404)
    def not_found(_error):
        return create_output_on_error(AppErrorCode.APP_NOT_FOUND_ERROR)

    @rest_app.errorhandler(405)
    def not_found(_error):
        return create_output_on_error(AppErrorCode.APP_METHOD_NOT_ALLOWED)

    @rest_app.errorhandler(422)
    def unprocessable(_error):
        return create_output_on_error(AppErrorCode.APP_UNPROCESSABLE_ERROR)

    @rest_app.errorhandler(429)
    def too_many_requests(_error):
        return create_output_on_error(AppErrorCode.APP_TOO_MANY_REQUESTS_ERROR)

    @rest_app.errorhandler(500)
    def server_error(_error):
        return create_output_on_error(AppErrorCode.APP_UNKNOWN_ERROR)

    @rest_app.errorhandler(502)
    def bad_gateway(_error):
        return create_output_on_error(AppErrorCode.APP_BAD_GATEWAY_ERROR)

    @rest_app.errorhandler(503)
    def service_unavailable(_error):
        return create_output_on_error(AppErrorCode.APP_SERVICE_UNAVAILABLE_ERROR)

    logger.info('REST API STARTING')

    # socket_io.run(rest_app, host=host, port=port, debug=debug, use_reloader=False, threaded=True, ssl_context=ssl)
    rest_app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True, ssl_context=ssl)
    # socket_io.run(rest_app)


def start_rpc_daemon():
    """
    Start RPC Daemon
    """

    logger.info('RPC DAEMON STARTING')

    # Run the daemon’s request loop to make pyro4 wait for incoming requests
    rpc_daemon.requestLoop()


@auth.verify_password
def verify_password(user_or_token, _password):
    """
    Check authentication for flask. It'll use auth module.
    Automatically called when executed api method.

    :param user_or_token: username/token
    :param _password: user's password
    """

    # Get module object from rpc and execute check_token method
    try:
        auth_module = get_module('auth_module')
        return auth_module.check_token(user_or_token)
    except AppException as e:
        return create_output_on_error(e.error_code)


# Create dictionary with all modules: infrastructure and product modules

infra_modules = get_infra_modules()

# Get product summary module class as string from configuration and then import dynamically
# It uncouples product modules from the original code
product_summary_file = config.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.APP_MODULES_SUMMARY)
product_module_summary = importlib.import_module(product_summary_file)
product_modules = product_module_summary.get_product_modules()

# Join two dictionaries
module_names = {**infra_modules, **product_modules}
