from common import config

from common.module_manager import get_module
from sky_modules.forensic_module import MODULE_NAME
from sky_modules.sky_module import SkyModule

logger = config.get_log(MODULE_NAME)


class ForensicModule(SkyModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """
