import time
from nose.tools import assert_equal, assert_true, assert_is_not_none

from common import config
from common.infra_modules.database_module.database_module import DatabaseModule



class TestDatabaseModule(object):
    module = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """
        # TestDatabaseObjectModule.module = DatabaseObjectModule()
        TestDatabaseModule.module = DatabaseModule(config, 'database_module')

    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """

    def setup(self):
        """
        This method is run once before _each_ test method is executed
        """

    def teardown(self):
        """
        This method is run once after _each_ test method is executed
        """

    def test_1_exec_query(self) -> None:
        """
        Execute raw select query
        """

        query = 'select * from employees'
        out = self.module.exec_query(query)
        assert_true(len(out) >= 0)


    def test_2_exec_query(self) -> None:
        """
        Execute raw update query
        """

        query = 'update employees set State="SS"'
        out = self.module.exec_query(query)
        assert_true(len(out) >= 0)


    def test_3_insert(self) -> None:
        """
        Execute insert query
        """

        data = {'Name': 'PEPE'}
        out = self.module.insert('genres', data)
        assert_true(out)


    def test_4_read(self) -> None:
        """
        Execute select query
        """

        filter = 'Name like "C%"'
        out = self.module.read('genres', filter)
        assert_true(len(out) >= 0)


    def test_5_update(self) -> None:
        """
        Execute insert query
        """

        data = {'Name': 'KKKK'}
        filter =  'Name="PEPE"'
        out = self.module.update('genres', data, filter)
        assert_true(out)


    def test_5_delete(self) -> None:
        """
        Execute select query
        """

        filter = 'Name like "C%"'
        out = self.module.delete('genres', filter)
        assert_true(out)
