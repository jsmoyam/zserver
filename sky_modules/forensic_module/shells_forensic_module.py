import sky_modules
from common import config
from common.infra_tools.parser_tools import get_args_from_shell

from sky_modules.forensic_module import MODULE_NAME

logger = config.get_log(MODULE_NAME)


class ForensicModuleShell:

# All commands must start with "shell_" to be published
# Arguments of commands are tuple of tuple: ((arg1, arg2, arg3))
# Arguments are recovered with get_args_from_shell method
# Help methods must star with "help_" and command name
# Category are defined in category method

    def category_forensic_module_shell(self) -> dict:
        # Dictionary with commands and category text
        return {
            'fst': sky_modules.module_shell_summary.CAT_FORENSIC,
            'regripper': sky_modules.module_shell_summary.CAT_FORENSIC
        }

    def shell_fst(self, args: tuple):
        device, connection_mode = get_args_from_shell(args)

        # Call to main module method

        logger.info('fst: {}'.format(device))
        return 'fst'

    def help_fst(self, args):
        return 'This is a help for fst command'

    def shell_regripper(self, args: tuple):
        mount_point, connection_mode = get_args_from_shell(args)

        # Call to main module method

        logger.info('regripper mount_point: {}'.format(mount_point))
        return 'regripper'

    def help_regripper(self, args):
        return 'This is a help for regripper command'
