from concurrent.futures import ThreadPoolExecutor

from common import config
from common.app_config import AppConfig
from common.app_model import AppException, GenericErrorMessages
from common.module_manager import get_module, get_all_modules, add_module, add_remote_module, expose_module, \
    start_api, start_rpc


def main():
    logger = config.get_log(AppConfig.MAIN_CONFIGURATION)

    logger.info('INIT MODULES')

    # Check if rpc is active
    rpc_active = config.is_value_active(AppConfig.MAIN_CONFIGURATION, AppConfig.RPC_ACTIVE)

    # Read config and build all active modules
    section_modules = config.get_sections()
    for section_module in section_modules:
        try:
            active = config.is_value_active(section_module, AppConfig.ACTIVE)
        except AppException:
            active = False

        if rpc_active:
            try:
                remote = config.is_value_active(section_module, AppConfig.REMOTE)
                connect_exposed_module = config.get_value(section_module, AppConfig.CONNECT_EXPOSED_MODULE)
            except AppException:
                remote = False

        if active:
            # Create an instance and  store in dictionary
            add_module(config, section_module)

            # Expose module from remote procedure call
            if rpc_active:
                try:
                    exposed_module = config.is_value_active(section_module, AppConfig.EXPOSED)

                    try:
                        if exposed_module:
                            exposed_name = config.get_value(section_module, AppConfig.EXPOSED_NAME)
                            expose_module(section_module, exposed_name)
                    except AppException:
                        logger.error(GenericErrorMessages.EXPOSED_CONFIGURATION_ERROR)
                        logger.error('Module {} not exposed'.format(section_module))
                        raise AppException()

                except AppException:
                    pass

        elif rpc_active and remote:
            add_remote_module(section_module, connect_exposed_module)

    logger.info('ALL MODULES STARTED')

    # Init flask in thread. This implies use_reloader=False in flask
    # Init remote procedure calls with pyro4
    executor = ThreadPoolExecutor(2)
    executor.submit(start_api)
    executor.submit(start_rpc)


if __name__ == "__main__":
    main()
