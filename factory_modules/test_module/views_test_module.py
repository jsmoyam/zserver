import logging
import random
import time

from flask_socketio import Namespace, emit
from common.module import socket_io

import common
from common.module import ViewModule, authenticate
from common.infra_tools.decorators import log_function
from common.infra_modules.infra_exception import AppException

from factory_modules.test_module import MODULE_NAME
from factory_modules.test_module.model_test_module import TestSchema, TestData, TestResult, Test2Data, \
    Test1InputDataSchema, Test1InputData

logger = logging.getLogger(MODULE_NAME)


# @authenticate()
class TestModule1View(ViewModule):

    class MyCustomNamespace(Namespace):
        def on_connect(self):
            print('[namespace] connect')
            pass

        def on_disconnect(self):
            print('[namespace] disconnect')
            pass

        def on_my_event(self, data):
            print('[namespace] my event: {}'.format(data))
            emit('my_response', data)

        def on_my_personal_event(self, data):
            print('[namespace] my personal event: {}'.format(data))
            # emit('my_personal_response', data)
            for i in range(10):
                time.sleep(5)
                emit('my_personal_response', 'dato enviado')

    socket_io.on_namespace(MyCustomNamespace('/test'))

    @log_function(logger)
    def index(self):
        # For testing: curl --user TOKEN:nopass -X GET http://localhost:5000/test1
        # TOKEN is recovered from curl -d '{"username":"user", "password":"pass"}' -H "Content-type: application/json" -X POST http://localhost:5000/auth/login/
        self.app_module.example_method()
        logger.info('It will return "Hola mundo 1"')
        # dom = common.module.get_module('database_object_module')
        # dom.exit()

        return 'Hola múndo 1'

    @log_function(logger)
    def get(self, id):
        t2 = Test2Data([True, False])
        t1 = TestData(id, id, ['zzz', 'xxx', 'ccc'], [t2])

        aaa = [t1, t1]

        code = 'CODE_OK'
        msg = 'database.evidence.notfound'

        result = self.app_module.create_output(TestResult, TestSchema, aaa, code, msg=msg)
        return result

    @log_function(logger)
    def post(self):
        # For testing: curl -d '{"data1":"987987", "data2":"678678"}' -H "Content-type: application/json" -X POST http://localhost:5000/test1/
        # Create object from request
        input_data = self.app_module.create_input(Test1InputData, Test1InputDataSchema)

        self.app_module.example_method()

        # Process data to generate processed object
        t2 = Test2Data([True, False])
        t1 = TestData(input_data.data1, input_data.data2, t2, ['zzz', 'xxx', 'ccc'], [t2, t2])

        # Convert output object to result object
        result = self.app_module.create_output(TestResult, TestSchema, t1, 'CODE_OK', msg='database.evidence.notfound')
        return result

    @log_function(logger)
    def put(self, id):
        return self.app_module.create_output(TestResult, None, 'This is PUT with id {}\n'.format(id), 'CODE_OK')

    @log_function(logger)
    def random(self):
        """
        This api is accesible in http://ip:port/test1/random
        :return: str
        """

        num = '{}'.format(random.random())
        num = random.random()

        return self.app_module.create_output(TestResult, None, num, 'CODE_OK')


class TestModule2View(ViewModule):

    def index(self):
        return 'Hola mundo 2'