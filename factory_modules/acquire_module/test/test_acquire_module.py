import logging
import time
from nose.tools import assert_equal, assert_true
from common import config
from factory_modules.acquire_module.acquire_module import *
from common.infra_tools.decorators import log_function
from factory_modules.acquire_module.model_acquire_module import *
logger = logging.getLogger(MODULE_NAME)

terminal_existent = AcquireInputData('motorola1', 'qa1', 'terminal2')
terminal_inexistent = AcquireInputData('motorola', 'qa', 'terminal1')

tasks_list = (AcquireInputData('a', 'a', 'a'), AcquireInputData('b', 'b', 'b'), AcquireInputData('c', 'c', 'c'), AcquireInputData('d', 'd', 'd'))

file_to_get_inexistent = 'pepito.e01'
file_to_get_existent = 'jaimito.e01'

class TestAcquireModule(object):
    module = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """
        #TestDatabaseObjectModule.module = DatabaseObjectModule(config, 'database_object')
        TestAcquireModule.module = AcquireModule(config, 'acquire_module')

    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """
        pass

    def setup(self):
        """
        This method is run once before _each_ test method is executed
        """

        pass

    def teardown(self):
        """
        This method is run once after _each_ test method is executed
        """
        pass

    @log_function(logger)
    def test_1_get_acquired_tasks(self):
        """
        Recuperar lista de tareas
        """

        result = self.module.get_acquired_tasks()
        assert_true(type(result) is list)

        pass

    @log_function(logger)
    def test_2_get_task(self):
        """
        Recuperar tarea pasandole una lista de ids
        """
        for task in range(0,100):
            result = self.module.get_task(str(task))
            if not result:
                return False
        assert_true(result)
        pass

    @log_function(logger)
    def test_3_acquire_existent(self):
        """
        Probar a adquirir un terminal que existe
        """
        result = self.module.acquire(terminal_existent)
        assert_true(type(result) is AcquireData)
        pass


    @log_function(logger)
    def test_4_acquire_inexistent(self):
        """
        Probar a adquirir un terminal que no existe
        """
        result = self.module.acquire(terminal_inexistent)
        assert_equal(result is False)
        pass

    @log_function(logger)
    def test_5_get_size_ewf_inexistent(self):
        """
        Probar a obtener el tamaño de una evidencia inexistente
        """
        result = self.module.get_size_ewf('/repository/acquisitions/'+file_to_get_inexistent)
        assert(result)
        if result:
            return True
        return False

    @log_function(logger)
    def test_6_get_size_ewf_existent(self):
        """
        Probar a obtener el tamaño de una evidencia inexistente
        """
        result = self.module.get_size_ewf('/repository/acquisitions/'+terminal_existent.alias)
        assert_true(result==True)
        pass

    # @log_function(logger)
    # def test_7_put_get_task(self):
    #     """
    #     Probar a añadir una tarea y posteriormente adquirirla
    #     """
    #     input_data = self.module.create_input(terminal_existent, terminal_existent)
    #     acquire_data = self.module.acquire(input_data)
    #     # TODO comprobar cómo obtener el id de la tarea creada en concreto
    #     #result = self.module.get_task(str(task))
    #
    #     pass
    #

    # @log_function(logger)
    # def test_8_put_get_tasks(self):
    #     """
    #     Probar a añadir una lista de tareas y posteriormente adquirirlas
    #     """
    # TODO: Adquirir id de las tareas previamente subidas
    #     for task in tasks_list:
    #
    #         a = self.module.acquire(task)
    #     result = self.module.get_acquired_tasks()
    #     assert(result)
    #     if result:
    #         return True
    #
    #     return False


    # @log_function(logger)
    # def test_9_put_clean_adquisition(self) -> bool:
    #     """
    #     Probar a eliminar una adquisición previamente añadida
    #     """
    # TODO:
    #     adquire = self.module.create_input(terminal_existent, terminal_existent)
    #     aux = self.module.acquire(adquire)
    #     result = self.module.clean_acquisition('/repository/acquisitions/'+file_to_get_existent.alias)
    #     assert(result)
    #     if result:
    #         return True
    #
    #     return False



    @log_function(logger)
    def test_10_check_queue_previously_launched(self) -> None:
        """
        Comprobar que se obtiene una lista de tareas previamente lanzadas
        """
        self.module.acquire(self.module.create_input(terminal_existent, terminal_existent))
        result = self.module.get_acquired_tasks()
        assert_true(result)
        pass


    @log_function(logger)
    def test_11_clean_directory_empty(self) -> None:
        """
        Comprobar a borrar un directorio que no existe
        """
        result = self.module.clean_acquisition('/repository/acquisitions/aaaaaa')
        assert_equal(result, False)
        pass


    @log_function(logger)
    def test_12_acquire_check_values(self):
        """
        Probar a adquirir y luego comprobar la integridad de los campos
        """
        result = self.module.acquire(terminal_existent)
        assert_true(type(result) is AcquireData)
        pass

