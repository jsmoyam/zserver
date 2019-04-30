from common import config
from common.infra_modules.infra_module import InfraModule
from common.infra_tools.decorators import log_function
from common.infra_modules.virt_module import MODULE_NAME
from common.infra_modules.virt_module.model_virt_module import VirtException, VirtMachineData
from common.infra_modules.virt_module.impl.virt_api import VirtApi
from common.infra_modules.virt_module.impl.virt_api_factory import VirtApiFactory

from common.infra_modules.virt_module.views_virt_module import VirtModuleView
logger = config.get_log(MODULE_NAME)


class VirtModule(InfraModule):
    """
    Main class of virtualization module
    """

    def initialize(self):
        """
        Get configuration and connection object
        """
        self.register_url(VirtModuleView, '/virt')
        self.virt_sw = self.module_config.get_value(MODULE_NAME, 'virt_sw')
        self.virt_connection = self.module_config.get_value(MODULE_NAME, 'virt_connection')
        self.virt = VirtApiFactory.get_connection(self.virt_sw, self.virt_connection)

    def exit(self) -> None:
        logger.info('SHUTDOWN MODULE')

    @log_function(logger)
    def get_stats_virtual_machine(self, ids_vm: list) -> list:
        """
        Get ram, disk data in virtual machine from virtualization software
        :param id_vm: virtual machine id
        :return: list of VirtMachineData object
        """

        try:
            ret = self.virt.get_stats_virtual_machine(ids_vm)
            return ret
        except VirtException as e:
            logger.error('Error recovering data from virtualization system', exc_info=True)
            return None

    @log_function(logger)
    def get_stats_infrastructure(self) -> VirtMachineData:
        """
        Get ram, disk data in virtualization infrastructure
        :return: VirtMachineData object
        """

        try:
            ret = self.virt.get_stats_infrastructure()
            return ret
        except VirtException as e:
            logger.error('Error recovering data from virtualization system', exc_info=True)
            return None
