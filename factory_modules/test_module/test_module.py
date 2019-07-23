from common import config

import common
from factory_modules.test_module import MODULE_NAME
from factory_modules.factory_module import FactoryModule
from factory_modules.test_module.views_test_module import TestModule1View, TestModule2View

logger = config.get_log(MODULE_NAME)


class TestModule(FactoryModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """
        self.register_url(TestModule1View, '/test1')
        self.register_url(TestModule2View, '/test2')

    def example_method(self):
        logger.info('Example call')
        print('Example call')
        # db = common.module_manager.get_module('database_module')
        # ret = db.exec_query('SELECT 1')
        # logger.info(ret)
        # dom = common.module_manager.get_module('database_object_module')
        # dom.exit()