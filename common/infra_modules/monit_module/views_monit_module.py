import logging
import json

from typing import Dict, Union

from common.module import ViewModule, authenticate
from common.infra_tools.decorators import log_function
from common.infra_modules.monit_module import MODULE_NAME
from common.infra_modules.monit_module.model_monit_module import MonitResult, ShutdownSchema, ShutdownData


logger = logging.getLogger(MODULE_NAME)


@authenticate()
class MonitModuleView(ViewModule):
    excluded_methods = ["get_system_statistics_response_json"]

    # TODO: Esto no puede hacerse de esta manera. Hay que hacerlo con create_output.

    # get_system_statistics
    @log_function(logger, print_result=False)
    def system_statistics(self) -> str:
        system_statistics = self.app_module.get_system_statistics()

        return json.dumps(system_statistics)

        #return self.get_system_statistics_response_json(system_statistics)



    """
    def get_system_statistics_response_json(self, system_statistics: Dict[str, Union[int, float]]) -> str:
        if not system_statistics:
            system_statistics_result_data = None
        else:
            system_statistics_result_data = RepositoriesResultData(system_statistics)

        return self.app_module.create_output(TreeModuleResponse, RepositoriesResultSchema, system_statistics_result_data, repositories_response.get("status"), msg=repositories_response.get("message_id"))
    """

# @authenticate()
class ShutdownMonitModuleView(ViewModule):

    @log_function(logger, print_result=False)
    def get(self, when: str) -> str:
        out = self.app_module.shutdown(when)
        if out.success:
            code = 'CODE_OK'
            msg = ''
        else:
            code = 'CODE_KO'
            msg = 'Can not shutdown machine'

        result = self.app_module.create_output(MonitResult, ShutdownSchema, out, code, msg=msg)
        return result