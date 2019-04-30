import psutil

import common
from common import config
from common.module import stop_rest_app
from common.infra_modules.infra_module import InfraModule
from common.infra_tools.decorators import log_function
from common.infra_tools.task_thread import TaskThread
from common.infra_tools.parser_tools import striplist
from common.infra_tools.expression_evaluator_tool.expression_evaluator import ExpressionEvaluator
from common.infra_modules.monit_module import MODULE_NAME
from common.infra_modules.monit_module.views_monit_module import MonitModuleView, ShutdownMonitModuleView
from common.infra_modules.monit_module.model_monit_module import CpuStatData, RamStatData, SwapStatData, \
    DiskStatData, SystemStatData, RuleData, ServerData, AdditionalServerData
from common.infra_modules.monit_module.model_monit_module import ShutdownData


logger = config.get_log(MODULE_NAME)

RULE_PREFIX = 'rule-'
CONDITIONS_MODULE = 'common.infra_modules.monit_module.conditions_monit_module'
ACTIONS_MODULE = 'common.infra_modules.monit_module.actions_monit_module'


class MonitModule(InfraModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """

        # Load system_commands_module
        try:
            self.scm = common.module_manager.get_module('system_commands_module')
        except Exception as e:
            logger.error('Can not import system_commands_module')
            logger.exception(e)

        # Load specific config file
        sections = config.get_sections(config_type=MODULE_NAME)

        # Recover rules
        all_rules = dict()
        for section in sections:
            if section.startswith(RULE_PREFIX):
                rule_name = section[section.index(RULE_PREFIX) + len(RULE_PREFIX):]
                condition = config.get_value(section, 'condition', MODULE_NAME)
                action_ok = config.get_value(section, 'action_ok', MODULE_NAME)
                action_ko = config.get_value(section, 'action_ko', MODULE_NAME)

                rule_data = RuleData(rule_name, condition, action_ok, action_ko)
                rule_data.condition_evaluator = ExpressionEvaluator(condition)
                rule_data.condition_evaluator.add_function_package(CONDITIONS_MODULE)
                rule_data.action_ok_evaluator = ExpressionEvaluator(action_ok)
                rule_data.action_ok_evaluator.add_function_package(ACTIONS_MODULE)
                rule_data.action_ko_evaluator = ExpressionEvaluator(action_ko)
                rule_data.action_ko_evaluator.add_function_package(ACTIONS_MODULE)
                all_rules[rule_name] = rule_data

        # Create server data with associated rules
        servers = dict()
        for section in sections:
            if not section.startswith(RULE_PREFIX):
                server_name = section
                host = config.get_value(section, 'host', MODULE_NAME)
                port = config.get_value(section, 'port', MODULE_NAME)
                username = config.get_value(section, 'username', MODULE_NAME)
                password = config.get_value(section, 'password', MODULE_NAME)
                interval = int(config.get_value(section, 'interval', MODULE_NAME))
                applied_rules = striplist(config.get_value(section, 'rules', MODULE_NAME).split(','))
                rules = [all_rules[x] for x in applied_rules]

                server_data = ServerData(server_name, host, port, username, password, interval, rules)
                server_data.host_evaluator = ExpressionEvaluator(host)
                server_data.host_evaluator.add_function_package(CONDITIONS_MODULE)
                servers[server_name] = server_data

        # Init and execute threads. Store task in dictionary indexed by server name
        self.check_tasks = dict()
        for server in servers.values():
            server_check_task = self.ServerCheckTask(server)
            self.check_tasks[server.name] = server_check_task
            server_check_task.set_interval(server.interval)
            server_check_task.setName(server.name)
            server_check_task.set_initial_delay(int(config.get_value(MODULE_NAME, 'initial_delay')))
            server_check_task.start()

        self.register_url(MonitModuleView, '/monit')
        self.register_url(ShutdownMonitModuleView, '/shutdown')

    def stop_all_server_check_task(self):
        """Stop server check periodic tasks"""
        for server_name, task in self.check_tasks.items():
            task.shutdown()

    @log_function(logger)
    def get_stats(self) -> SystemStatData:
        """Get all data from system. All sizes are in bytes and percentage"""

        # Get cpu data
        cpu_stat = CpuStatData()
        cpu_stat.cpu_percent_usage = psutil.cpu_percent(interval=0.1)

        # Get ram data
        ram_stat = RamStatData()
        memory_data = psutil.virtual_memory()
        ram_stat.ram_total_memory = memory_data.total
        ram_stat.ram_used_memory = memory_data.used
        ram_stat.ram_free_memory = memory_data.free
        ram_stat.ram_percent_usage_memory = memory_data.percent

        # Get swap data
        swap_stat = SwapStatData()
        swap_data = psutil.swap_memory()
        swap_stat.swap_total_memory = swap_data.total
        swap_stat.swap_used_memory = swap_data.used
        swap_stat.swap_free_memory = swap_data.free
        swap_stat.swap_percent_usage_memory = swap_data.percent

        # Get disk data
        disk_stats = list()
        partitions = psutil.disk_partitions()
        for partition in partitions:
            disk_stat = DiskStatData()
            disk_stat.disk_device = partition.device
            disk_stat.disk_mount_point = partition.mountpoint

            repository_stat = psutil.disk_usage(disk_stat.disk_mount_point)
            disk_stat.disk_total_memory = repository_stat.total
            disk_stat.disk_used_memory = repository_stat.used
            disk_stat.disk_free_memory = repository_stat.free
            disk_stat.disk_percent_usage_memory = repository_stat.percent

            disk_stats.append(disk_stat)

        # Collect system data in object
        stat = SystemStatData(cpu_stat, ram_stat, swap_stat, disk_stats)
        return stat

    @log_function(logger)
    def stop_rest(self):
        """ This methods stop rest api """
        stop_rest_app()

    @log_function(logger)
    def status(self):
        """ This method returns status of all modules"""
        # TODO
        pass

    @log_function(logger)
    def shutdown(self, when: str) -> ShutdownData:
        """
        Stop computer
        :param when: time to shutdown
        :return: object with result of shutdown
        """
        s = self.scm.shutdown(when)
        out = ShutdownData(s)
        return out

    class ServerCheckTask(TaskThread):
        """Task to check server rules"""
        def __init__(self, data: ServerData) -> None:
            TaskThread.__init__(self)
            self.data = data

        def task(self) -> None:

            # Evaluate hosts and apply the rule for all hostname servers
            hostnames = self.data.host_evaluator.evaluate({})

            # Loop for all rules in server
            for rule in self.data.rules:

                # Loop for all hostnames to apply the same rule
                for host in hostnames.split(','):

                    # Generate additional data for this host
                    additional_data = AdditionalServerData(self.data.name, host, self.data.port,
                                                           self.data.username, self.data.password)

                    rule.condition_evaluator.set_additional_data(additional_data)
                    result = rule.condition_evaluator.evaluate({})
                    additional_data.condition_result = result

                    logger.info('Rule {} condition {} applied to {} with result {}'.format(rule.name, rule.condition,
                                                                                           self.data.name, result))
                    if result:
                        rule.action_ok_evaluator.set_additional_data(additional_data)
                        rule.action_ok_evaluator.evaluate({})
                        logger.log(config.name_to_level[config.get_value(MODULE_NAME, 'action_ok_log_level')],
                                   'Rule OK {} applied to {}'.format(rule.name, self.data.name))
                    else:
                        rule.action_ko_evaluator.set_additional_data(additional_data)
                        rule.action_ko_evaluator.evaluate({})
                        logger.log(config.name_to_level[config.get_value(MODULE_NAME, 'action_ko_log_level')],
                                   'Rule KO {} applied to {}'.format(rule.name, self.data.name))
