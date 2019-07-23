from common import config

from common.module_manager import get_module
from factory_modules.forensic_module import MODULE_NAME
from factory_modules.factory_module import FactoryModule

logger = config.get_log(MODULE_NAME)


class ForensicModule(FactoryModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """
