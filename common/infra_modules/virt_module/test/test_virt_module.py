import time
from nose.tools import assert_equal, assert_true, assert_is_not_none

from common import config
from common.infra_modules.virt_module.virt_module import VirtModule
from common.infra_modules.virt_module.model_virt_module import VirtInfraData


class TestVirtModule(object):
    module = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """
        # TestDatabaseObjectModule.module = DatabaseObjectModule()
        TestVirtModule.module = VirtModule(config, 'virt_module')

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

    def test_1_get_stats_virtual_machine(self) -> None:
        """
        Get data from virtual machine
        """

        # List with an existent id and an inexistent id.
        vms = ['andromeda01-dev', 'inexistent-machine']
        # Call the method to test
        stats = self.module.get_stats_virtual_machine(vms)
        # Check if the result list has 2 items.
        assert_true(len(stats) == 2)
        # Check the name of the first result
        assert_true(stats[0].name == vms[0])
        # Check the length of the first result disks list
        assert_true(len(stats[0].disks) > 0)
        # Check that the ram assigned for the first result is greater than 0
        assert_true(stats[0].ram_assigned > 0)
        # Check that the result for an inexistent machine is None
        assert_true(stats[1] is None)


    def test_2_get_stats_infrastructure(self) -> None:
        """
        Get data from infrastructure
        """
        # Call the method to test.
        stats = self.module.get_stats_infrastructure()
        # Check the type of the object returned.
        assert_true(type(stats) == VirtInfraData)
        # Check that the 'total' stats are greater than 0.
        assert_true(stats.cpu_total > 0)
        assert_true(stats.disk_total > 0)
        assert_true(stats.memory_total > 0)
