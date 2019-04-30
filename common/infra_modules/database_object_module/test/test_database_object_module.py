import time
from nose.tools import assert_equal, assert_true

from common import config
from common.infra_modules.database_object_module.data_model import DatabaseObject, DatabaseObjectResult
from common.infra_modules.database_object_module.database_object_module import DatabaseObjectModule
from common.infra_modules.database_object_module.impl.access_database import AccessDatabase


class DatabaseObjectTest1(DatabaseObject):

    def __init__(self) -> None:
        DatabaseObject.__init__(self)
        self.value = 1
        self.bool_arg_2 = bool(False)

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class DatabaseObjectTest2(DatabaseObject):

    def __init__(self, user_arg=0) -> None:
        DatabaseObject.__init__(self)
        self.user_arg = user_arg
        self.int_arg = int(5)
        self.bool_arg = bool(False)
        self.str_arg = str('cadena de texto')
        self.list_arg = ['one thing', 'another thing']
        self.float_arg = float(7.9)
        self.dict_arg = {'key1': 'value1', 'key2': 'value2'}

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class DatabaseObjectTest3(DatabaseObject):

    def __init__(self, user_arg='') -> None:
        DatabaseObject.__init__(self)
        self.user_arg = user_arg
        self.int_arg = int(10)
        self.bool_arg = bool(True)
        self.bool_arg_2 = bool(False)
        self.str_arg = str('otra cadena de texto')
        self.list_arg = [True, 'hola', 5]
        self.float_arg = float(7.9)
        self.dict_arg = {'k1': 'v1', 'k2': 'v2', 'k3': 7}

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class DatabaseObjectTest4(DatabaseObject):

    def __init__(self, user_arg=0) -> None:
        DatabaseObject.__init__(self)
        self.user_arg = user_arg
        self.int_arg = int(5)
        self.bool_arg = bool(False)
        self.str_arg = str('cadena de texto')
        self.list_arg = ['one thing', 'another thing']
        self.float_arg = float(7.9)
        self.dict_arg = {'key1': 'value1', 'key2': 'value2'}

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class DatabaseObjectTestError(object):

    def __init__(self) -> None:
        self.value = 1

    def __repr__(self):
        return str(self.__dict__)


class TestDatabaseObjectModule(object):
    module = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """
        # TestDatabaseObjectModule.module = DatabaseObjectModule()
        TestDatabaseObjectModule.module = DatabaseObjectModule(config, 'database_object')

    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """
        TestDatabaseObjectModule.module.exit()

    def setup(self):
        """
        This method is run once before _each_ test method is executed
        """

        data_1 = DatabaseObjectTest1()
        data_2 = DatabaseObjectTest2()
        schema = 'TEST'
        object_name_1 = data_1.__class__.__name__
        object_name_2 = data_2.__class__.__name__
        self.module.remove(schema, object_name_1)
        self.module.remove(schema, object_name_2)
        print('Deleted all data')

    def teardown(self):
        """
        This method is run once after _each_ test method is executed
        """

    def test_1_put_get(self) -> None:
        """
        Insercion de objeto y recuperacion por id para verificar que se inserto correctamente
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        result_put = self.module.put_object(schema, object_name, data)
        inst_put = result_put.get_object_from_data()
        id_put = inst_put[0].get_identifier()

        result_get = self.module.get(schema, object_name, [(AccessDatabase.ID_FIELD, '=', id_put)])
        inst_get = result_get.get_object_from_data(DatabaseObjectTest2())
        id_get = inst_get[0].get_identifier()

        assert_equal(id_put, id_get)

    def test_2_put_get_multiple(self) -> None:
        """
        Insercion de muchos objectos y recuperacion por id para verificar que se inserto correctamente
        """

        max_iteration = 10

        insert_id_list = list()
        get_id_list = list()

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2()
            result_put = self.module.put_object(schema, object_name, data)

            assert_equal(result_put.code, DatabaseObjectResult.CODE_OK)
            inst_put = result_put.get_object_from_data()
            id_put = inst_put[0].get_identifier()
            insert_id_list.append(id_put)

        for insert_id in insert_id_list:
            result_get = self.module.get(schema, object_name, [(AccessDatabase.ID_FIELD, '=', insert_id)])

            assert_equal(result_get.code, DatabaseObjectResult.CODE_OK)
            inst_get = result_get.get_object_from_data()
            id_get = inst_get[0].get_identifier()
            get_id_list.append(id_get)

        assert_equal(insert_id_list, get_id_list)
        assert_equal(len(insert_id_list), max_iteration)

    def test_3_put_get_multiple(self) -> None:
        """
        Insercion de muchos objectos y recuperacion de todos.
        """

        max_iteration = 10

        insert_id_list = list()

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2()

            start = time.perf_counter()
            result_put = self.module.put_object(schema, object_name, data)
            elapsed_time = round((time.perf_counter() - start) * 1000, 2)
            # print("Insertion {} time {} ms.".format(i, elapsed_time))

            assert_equal(result_put.code, DatabaseObjectResult.CODE_OK)

            inst_put = result_put.get_object_from_data()
            id_put = inst_put[0].get_identifier()
            insert_id_list.append(id_put)

        start = time.perf_counter()
        result_get = self.module.get(schema, object_name)
        elapsed_time = round((time.perf_counter() - start) * 1000, 2)
        print("Total results obtained {} in {} ms.".format(max_iteration, elapsed_time))

        start = time.perf_counter()
        inst_get = result_get.get_object_from_data()
        elapsed_time = round((time.perf_counter() - start) * 1000, 2)
        print("Total objects obtained {} in {} ms.".format(max_iteration, elapsed_time))

        assert_equal(len(inst_get), max_iteration)

    def test_4_put_error(self) -> None:
        """
        Insercion de objeto y fallo al insertar
        """

        data = DatabaseObjectTestError()
        schema = 'TEST'
        object_name = data.__class__.__name__

        result = self.module.put_object(schema, object_name, data)
        assert_equal(result.code, DatabaseObjectResult.CODE_KO)

    def test_5_get(self) -> None:
        """
        Insercion de objeto y recuperacion fallida
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        self.module.put_object(schema, object_name, data)

        result_module = self.module.get(schema, object_name, [('int_arg', '=', 'wrong_value')])
        result = result_module.get_object_from_data(DatabaseObjectTest2())

        assert_true(len(result) == 0)

    def test_6_get(self) -> None:
        """
        Insercion de objeto y recuperacion por atributo entero
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        self.module.put_object(schema, object_name, data)

        result_get = self.module.get(schema, object_name, [('int_arg', '=', 5)])
        result = result_get.get_object_from_data(DatabaseObjectTest2())

        assert_equal(result[0].int_arg, data.int_arg)

    def test_7_get(self) -> None:
        """
        Insercion de objeto y recuperacion por atributo bool
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        result_put = self.module.put_object(schema, object_name, data)
        inst_put = result_put.get_object_from_data()
        id_put = inst_put[0].get_identifier()

        result_get = self.module.get(schema, object_name, [('bool_arg', '=', False)])
        inst_get = result_get.get_object_from_data()
        id_get = inst_get[0].get_identifier()

        assert_equal(id_put, id_get)

    def test_8_get(self) -> None:
        """
        Insercion de objeto y recuperacion por atributo string
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        result_put = self.module.put_object(schema, object_name, data)
        inst_put = result_put.get_object_from_data()
        id_put = inst_put[0].get_identifier()

        result_get = self.module.get(schema, object_name, [('str_arg', '=', 'cadena de texto')])
        inst_get = result_get.get_object_from_data(DatabaseObjectTest2())
        id_get = inst_get[0].get_identifier()

        assert_equal(id_put, id_get)

    def test_9_get(self) -> None:
        """
        Insercion de objeto y recuperacion por atributo float
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        result_put = self.module.put_object(schema, object_name, data)
        inst_put = result_put.get_object_from_data()
        id_put = inst_put[0].get_identifier()

        result_get = self.module.get(schema, object_name, [('float_arg', '=', 7.9)])
        inst_get = result_get.get_object_from_data(DatabaseObjectTest2())
        id_get = inst_get[0].get_identifier()

        assert_equal(id_put, id_get)

    def test_10_get(self) -> None:
        """
        Insercion de objeto y recuperacion por atributo list
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        result_put = self.module.put_object(schema, object_name, data)
        inst_put = result_put.get_object_from_data()
        id_put = inst_put[0].get_identifier()

        result_get = self.module.get(schema, object_name, [('list_arg', '=', ['one thing', 'another thing'])])
        inst_get = result_get.get_object_from_data(DatabaseObjectTest2())
        id_get = inst_get[0].get_identifier()

        assert_equal(id_put, id_get)

    def test_11_get(self) -> None:
        """
        Insercion de objeto y recuperacion por atributos multiples
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        result_put = self.module.put_object(schema, object_name, data)
        inst_put = result_put.get_object_from_data()
        id_put = inst_put[0].get_identifier()

        result_get = self.module.get(schema, object_name, [('int_arg', '=', 5), ('bool_arg', '=', False),
                                                           ('str_arg', '=', 'cadena de texto')])
        inst_get = result_get.get_object_from_data(DatabaseObjectTest2())
        id_get = inst_get[0].get_identifier()

        assert_equal(id_put, id_get)

    def test_12_get(self) -> None:
        """
        Insercion de objeto y recuperacion por atributos multiples
        """

        data = DatabaseObjectTest2()
        schema = 'TEST'
        object_name = data.__class__.__name__

        self.module.put_object(schema, object_name, data)

        result_get = self.module.get(schema, object_name, [('int_arg', '=', 5), ('bool_arg', '=', False),
                                                           ('str_arg', '=', 'XXXcadena de texto')])
        inst_get = result_get.get_object_from_data(DatabaseObjectTest2())

        assert_true(len(inst_get) == 0)

    def test_13_get(self) -> None:
        """
        Insercion de objeto y recuperacion por valor dentro de una lista
        """

        max_iteration = 10
        insert_id_list = list()
        list_arg = [5, 6, 7, 9]

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', 'in', list_arg)])
        inst_get = result_get.get_object_from_data()

        assert_true(len(inst_get) == len(list_arg))

    def test_14_get(self) -> None:
        """
        Insercion de objeto y recuperacion por valor fuera de una lista
        """

        max_iteration = 10
        insert_id_list = list()
        list_arg = [5, 6, 7, 9]

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', 'out', list_arg)])
        inst_get = result_get.get_object_from_data()

        assert_true(len(inst_get) == max_iteration - len(list_arg))

    def test_15_get(self) -> None:
        """
        Insercion de objeto y recuperacion por mqyor que
        """

        max_iteration = 10
        insert_id_list = list()
        number_to_compare = 6

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', '>', number_to_compare)])
        inst_get = result_get.get_object_from_data()

        assert_true(len(inst_get) == max_iteration - 1 - number_to_compare)

    def test_16_get(self) -> None:
        """
        Insercion de objeto y recuperacion por menor que
        """

        max_iteration = 10
        insert_id_list = list()
        number_to_compare = 6

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', '<', number_to_compare)])
        inst_get = result_get.get_object_from_data()

        assert_true(len(inst_get) == number_to_compare)

    def test_17_get(self) -> None:
        """
        Insercion de objeto y recuperacion por mayor o igual que
        """

        max_iteration = 10
        insert_id_list = list()
        number_to_compare = 6

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', '>=', number_to_compare)])
        inst_get = result_get.get_object_from_data()

        assert_true(len(inst_get) == max_iteration - number_to_compare)

    def test_18_get(self) -> None:
        """
        Insercion de objeto y recuperacion por menor o igual que
        """

        max_iteration = 10
        insert_id_list = list()
        number_to_compare = 6

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', '<=', number_to_compare)])
        inst_get = result_get.get_object_from_data()

        assert_true(len(inst_get) == number_to_compare + 1)

    def test_19_get(self) -> None:
        """
        Insercion de objeto y recuperacion por menor o igual que
        """

        max_iteration = 10
        insert_id_list = list()
        number_to_compare = 7

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', '!=', number_to_compare)])
        inst_get = result_get.get_object_from_data()

        assert_true(len(inst_get) == max_iteration - 1)

    def test_20_update(self) -> None:
        """
        Insercion de objeto, recuperacon y modificacion
        """

        max_iteration = 10
        insert_id_list = list()
        number_to_compare = 6

        schema = 'TEST'
        object_name = DatabaseObjectTest2.__name__
        for i in range(max_iteration):
            data = DatabaseObjectTest2(i)
            result_put = self.module.put_object(schema, object_name, data)
            insert_id_list.append(result_put.get_object_from_data()[0].get_identifier)

        result_get = self.module.get(schema, object_name, [('user_arg', '=', number_to_compare)])
        inst_get = result_get.get_object_from_data(obj=DatabaseObjectTest2())[0]

        inst_get.user_arg = 11
        result_update = self.module.update_object(schema, object_name, inst_get)

        assert_true(result_update.code == DatabaseObjectResult.CODE_OK)
