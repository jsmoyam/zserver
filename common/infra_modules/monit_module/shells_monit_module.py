import common.infra_modules
from common import config
from common.infra_tools.parser_tools import get_args_from_shell, get_app_version
from common.infra_modules.monit_module import MODULE_NAME


logger = config.get_log(MODULE_NAME)


class MonitModuleShell:

# All commands must start with "shell_" to be published
# Arguments of commands are tuple of tuple: ((arg1, arg2, arg3))
# Arguments are recovered with get_args_from_shell method
# Help methods must star with "help_" and command name
# Category are defined in category method

    def category_monit_module_shell(self) -> dict:
        # Dictionary with commands and category text
        return {
            'zappversion': common.infra_modules.module_shell_summary.CAT_VERSION_MANAGEMENT,
        }

    def shell_zappversion(self, args: tuple):
        try:
            return get_app_version()
        except:
            return 'Unknown'

    def help_zappversion(self, args):
        return 'Return application version name'
