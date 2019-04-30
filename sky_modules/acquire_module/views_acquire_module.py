import logging

from common.infra_tools.decorators import log_function
from common.module import ViewModule, authenticate
from sky_modules.acquire_module import MODULE_NAME
from sky_modules.acquire_module.model_acquire_module import AcquireInputData, AcquireInputDataSchema, AcquireData, \
    AcquireDataSchema, AcquireResult, AcquireDataListSchema, AcquireDataList


logger = logging.getLogger(MODULE_NAME)


#@authenticate()
class TestModule3View(ViewModule):


    @log_function(logger)
    def get(self, task_id):

        acquire_task = self.app_module.get_task(task_id)
        if acquire_task is None:
            code = 'CODE_OK'
            msg = 'acquisition.not_found'
            result = self.app_module.create_output(AcquireResult, None, None, code, msg=msg)
        else:
            code = 'CODE_OK'
            msg = 'acquisition.info'
            result = self.app_module.create_output(AcquireResult, AcquireDataSchema, acquire_task, code, msg=msg)
        return result

    @log_function(logger)
    def post(self):

        # Create object from request
        input_data = self.app_module.create_input(AcquireInputData, AcquireInputDataSchema)

        acquire_data = self.app_module.acquire(input_data)

        # Convert output object to result object
        result = self.app_module.create_output(AcquireResult, AcquireDataSchema, acquire_data, 'CODE_OK', msg='acquisition.started')
        return result

    @log_function(logger)
    def acquired_tasks(self):

        ready_list = self.app_module.get_acquired_tasks()
        if len(ready_list) != 0:
            code = 'CODE_OK'
            msg = 'acquisition.ready_list'
            acquire_data_list = AcquireDataList(ready_list)
            print(len(acquire_data_list.acquire_list))
            result = self.app_module.create_output(AcquireResult, AcquireDataListSchema, acquire_data_list, code, msg=msg)
        else:
            code = 'CODE_OK'
            msg = 'acquisition.no_ready_tasks'
            result = self.app_module.create_output(AcquireResult, None, None, code, msg=msg)
        return result
