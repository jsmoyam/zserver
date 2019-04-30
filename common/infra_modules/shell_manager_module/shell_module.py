import importlib

from common import config
from common.app_config import AppConfig
from common.infra_modules.module_shell_summary import get_infra_shells


logger = config.get_log(AppConfig.MAIN_CONFIGURATION)


class MetaShellModule(type):

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

        # Get infra and product shells

        infra_shell_modules = get_infra_shells()

        # Get product summary module class as string from configuration and then import dynamically
        product_shell_summary_file = config.get_value(AppConfig.MAIN_CONFIGURATION,
                                                      AppConfig.APP_PRODUCT_SHELL_SUMMARY_FILE)
        product_shell_module_summary = importlib.import_module(product_shell_summary_file)
        product_shell_modules = product_shell_module_summary.get_product_shells()

        # Join all shells in a list
        all_shells = infra_shell_modules + product_shell_modules

        # Iterate all module shells
        for shell in all_shells:
            # Get all public methods and attributes
            public_methods_and_attrs = [m for m in dir(shell) if not m.startswith('_')]

            # Get methods and assign to this class
            for method_name in public_methods_and_attrs:
                # Recover method or attribute
                method = getattr(shell, method_name)

                # Filter by method, discard attributes
                if callable(method):
                    attrs[method_name] = method

        attrs['__init__'] = auto_init
        return super(MetaShellModule, cls).__new__(cls, name, bases, attrs)
