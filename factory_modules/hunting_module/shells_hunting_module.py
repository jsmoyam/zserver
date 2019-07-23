import factory_modules
from common import config
from common.infra_tools.parser_tools import get_args_from_shell
from factory_modules.hunting_module import MODULE_NAME


logger = config.get_log(MODULE_NAME)


class HuntingModuleShell:
    pass

# All commands must start with "shell_" to be published
# Arguments of commands are tuple of tuple: ((arg1, arg2, arg3))
# Arguments are recovered with get_args_from_shell method
# Help methods must star with "help_" and command name
# Category are defined in category method

    # def category_test_module_shell(self) -> dict:
    #     # Dictionary with commands and category text
    #     return {
    #         'test1': factory_modules.module_shell_summary.CAT_TEST,
    #         'test2': factory_modules.module_shell_summary.CAT_TEST
    #     }
    #
    # def shell_test1(self, args: tuple):
    #     # arg1, arg2, connection_mode = get_args_from_shell(args)
    #     # logger.info('test_module test1 arg1: {} arg2: {}'.format(arg1, arg2))
    #     return 'test1'
    #
    # def help_test1(self, args):
    #     return 'This is a help for test1 command'
    #
    # def shell_test2(self, args: tuple):
    #     arg1, arg2, connection_mode = get_args_from_shell(args)
    #     logger.info('test_module test2 arg1: {} arg2: {}'.format(arg1, arg2))
    #     return 'test2'
