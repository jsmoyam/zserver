import logging

from common import config
from common.infra_modules.monit_module import MODULE_NAME
from common.infra_modules.system_commands_module.system_commands_module import SystemCommandsModule
from common.infra_modules.monit_module.conditions_monit_module import db_exec as db_exec_condition, \
    execute_shell as execute_shell_condition, \
    http_get as http_get_condition, http_get_with_condition_result as http_get_with_condition_result_condition

logger = config.get_log(MODULE_NAME)


def log(arg_list, additional_data):
    """Return True if empty"""
    if len(arg_list) == 0 or len(arg_list) > 2:
        logger.critical('Rule log action not well defined. Please check it')
    elif len(arg_list) == 1:
        logger.warning(arg_list[0])
    else:
        log_level = arg_list[1].upper()
        logger.log(config.name_to_level.get(log_level, logging.WARNING), arg_list[0])

    return True


def execute_shell(arg_list, additional_data):
    return execute_shell_condition(arg_list, additional_data)


def db_exec(arg_list, additional_data):
    return db_exec_condition(arg_list, additional_data)


def http_get(arg_list, additional_data):
    return http_get_condition(arg_list, additional_data)


def http_get_with_condition_result(arg_list, additional_data):
    return http_get_with_condition_result_condition(arg_list, additional_data)
