import time
from nose.tools import assert_equal, assert_true, assert_is_not_none

from common import config
from sky_modules.hunting_module.hunting_module import HuntingModule


class TestHuntingModule(object):
    module = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """
        TestHuntingModule.module = HuntingModule(config, 'hunting_module')

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


    def test_1_load_csv(self):
        full_path = '../common/infra_modules/parsing_module/test/files/test.csv'
        self.module.load_csv(full_path)


    def test_2_scopes_info(self):
        self.module.get_scope_data()


    def test_3_change_scopes_channel(self):
        channel1 = 'channel1'
        channel2 = 'channel2'
        self.module.update_machines_channel(channel1, channel2)
