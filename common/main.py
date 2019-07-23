from concurrent.futures import ThreadPoolExecutor

from common import config
from common.app_config import AppConfig
from common.app_model import AppException, AppErrorCode
from common.module_manager import add_module, add_remote_module, expose_module, start_api, start_rpc_daemon


def main():
    """
    Main method of the server. This check and instance all configured modules
    """

    # Get the app logger
    logger = config.get_log(AppConfig.APP_MAIN_CONFIGURATION)

    # Check if RPC is active
    rpc_active = config.is_value_active(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.RPC_ACTIVE)

    logger.info('INIT MODULES')

    # Read the configuration and get the different sections
    section_modules = config.get_sections(exclude_app=True)
    for section_module in section_modules:
        # Check if module is active
        try:
            is_active = config.is_value_active(section_module, AppConfig.ACTIVE)
        except AppException:
            is_active = False

        # If RPC is active in the app, get the configuration for this module
        remote = False
        connect_exposed_module = None
        if rpc_active:
            try:
                # Check if this module, it's a remote module
                remote = config.is_value_active(section_module, AppConfig.RPC_REMOTE_MODULE)
                # If it's a remote module, get the module's exposed name
                connect_exposed_module = config.get_value(section_module, AppConfig.RPC_CONNECT_EXPOSED_MODULE)
            except AppException:
                pass

        # If this modules is active
        if is_active:
            # Create an instance and  store in module manager dict
            add_module(config, section_module)

            # If RPC is active in the app, check if this module must be exposed
            if rpc_active:
                try:
                    exposed_module = config.is_value_active(section_module, AppConfig.RPC_MODULE_EXPOSED)

                    try:
                        if exposed_module:
                            # If it must be exposed, get the configuration for expose it
                            exposed_name = config.get_value(section_module, AppConfig.RPC_MODULE_EXPOSED_NAME)
                            # Expose it
                            expose_module(section_module, exposed_name)
                    except AppException:
                        logger.error(AppErrorCode.APP_CONF_MODULE_EXP.formatter(section_module))

                except AppException:
                    pass
        # If this modules is not active but RPC is active in the app
        # and this modules is a remote module, connect to this module
        # and add to module manager
        elif rpc_active and remote:
            add_remote_module(section_module, connect_exposed_module)

    logger.info('ALL MODULES STARTED')

    # Create two threads to init Flask and RPC (if it's active)
    executor = ThreadPoolExecutor(2) if rpc_active else ThreadPoolExecutor(1)
    # Init flask in thread. This implies use_reloader=False in flask
    executor.submit(start_api)

    if rpc_active:
        # Init remote procedure calls with pyro4. This required pyro-ns server
        executor.submit(start_rpc_daemon)


if __name__ == "__main__":
    main()
