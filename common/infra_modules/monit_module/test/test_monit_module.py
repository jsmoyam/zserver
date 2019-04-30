import time
import importlib
from nose.tools import assert_equal, assert_true, assert_false, raises

from common import config
from common.infra_modules.monit_module.model_monit_module import CpuStatData, RamStatData, SwapStatData, DiskStatData, \
    SystemStatData, AdditionalServerData
from common.infra_modules.monit_module.monit_module import MonitModule

from common.infra_tools.expression_evaluator_tool.expression_evaluator import ExpressionEvaluator
from common.infra_tools.expression_evaluator_tool.operations import Operations



class TestMonitModule(object):
    module = None

    def __init__(self):
        # Data for ssh connection
        self.ssh_host = 'jsmoya'
        self.ssh_port = 22
        self.ssh_username = 'admuser'
        self.ssh_password = 'Cyberp4d4w4n'


    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """

        TestMonitModule.module = MonitModule(config, 'monit')
        TestMonitModule.module.stop_all_server_check_task()


    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """
        TestMonitModule.module.stop_all_server_check_task()

    def setup(self):
        """
        This method is run once before _each_ test method is executed
        """

    def teardown(self):
        """
        This method is run once after _each_ test method is executed
        """

    def evaluate(self, expr: str, values: dict, insert_additional_data: bool):
        ev = ExpressionEvaluator(expr)
        ev.set_additional_data(AdditionalServerData('local', self.ssh_host, self.ssh_port,
                                                    self.ssh_username, self.ssh_password))
        ev.add_function_package('common.infra_modules.monit_module.conditions_monit_module')
        result = ev.evaluate(values)
        return result

    def test_1_get_stats(self) -> None:
        """
        Get all data from system
        """

        stats = self.module.get_stats()
        assert_true(stats.cpu_stat.cpu_percent_usage >= 0)

    def test_2_evaluate_condition(self) -> None:
        """
        Evaluate condition
        :return:
        """

        expr = 'is_empty[cadena]=True'
        values = {'cadena': 'hola'}
        result = self.evaluate(expr, values, False)
        assert_false(result)

    @raises(ValueError)
    def test_3_evaluate_http_get(self):
        """
        Evaluate condition http_get
        :return:
        """

        expr = 'http_get["http://localhost:50000/check_socket"]'
        result = self.evaluate(expr, {}, False)

    def test_4_evaluate_db_exec(self):
        """
        Evaluate condition db_exec
        :return:
        """

        expr = 'db_exec["sqlite:///test/chinook.db", "select Name from genres"] = "Rock"'
        result = self.evaluate(expr, {}, False)
        assert_true(result)

    def test_5_evaluate_execute_shell(self):
        """
        Evaluate condition db_exec
        :return:
        """

        expr = 'execute_shell["ls | wc -l", "False"] > "0"'
        result = self.evaluate(expr, {}, True)
        assert_true(result)

    def test_6_evaluate_used_space_percent(self):
        """
        Evaluate condition used_space_percent
        :return:
        """

        expr = 'used_space_percent["/"]>=0'
        result = self.evaluate(expr, {}, True)
        assert_true(result)

    def test_7_evaluate_used_space_percent_with_wildcards(self):
        """
        Evaluate condition used_space_percent with wildcards
        :return:
        """

        expr = 'check_used_space_percent["/dev/*", 90]'
        result = self.evaluate(expr, {}, True)
        assert_true(result==None)

    def test_8_evaluate_consumed_ram(self):
        """
        Evaluate condition consumed_ram
        :return:
        """

        expr = 'consumed_ram[]'
        result = self.evaluate(expr, {}, True)
        assert_true(result > 0)

    def test_9_evaluate_load_cpu(self):
        """
        Evaluate condition load_cpu
        :return:
        """

        expr = 'load_cpu[]'
        result = self.evaluate(expr, {}, True)
        assert_true(result > 0)
