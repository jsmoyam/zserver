import logging
from common.infra_tools.decorators import log_function
from common.module import ViewModule, authenticate
from common.infra_modules.virt_module.model_virt_module import VirtResult, VirtMachineListData, VirtMachineListDataSchema, VirtInfraData, VirtInfraDataSchema
from factory_modules.acquire_module import MODULE_NAME

logger = logging.getLogger(MODULE_NAME)

#@authenticate()
class VirtModuleView(ViewModule):

    # @log_function(logger)
    # def get(self):
    #     msg = "infra.data"
    #     infra_data = self.app_module.get_stats_infrastructure()
    #     result = self.app_module.create_output(VirtResult, VirtInfraDataSchema, infra_data, 'CODE_OK', msg=msg)
    #     return result


    @log_function(logger)
    def get(self):
        msg = "vm.data"
        lista = ['iron01-dev', 'nada']
        vms_data = self.app_module.get_stats_virtual_machine(lista)
        vms_obj = VirtMachineListData(vms_data)
        # TODO : Crear output de la nueva forma con HTTPresult.
        result = self.app_module.create_output(VirtResult, VirtMachineListDataSchema, vms_obj, 'CODE_OK', msg=msg)
        return result

