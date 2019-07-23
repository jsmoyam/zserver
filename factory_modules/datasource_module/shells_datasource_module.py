import factory_modules
from common.infra_tools.parser_tools import get_args_from_shell


class DatasourceModuleShell:

    def category_datasource_module_shell(self) -> dict:
        # Dictionary with commands and category text
        return {
            'database_example': factory_modules.module_shell_summary.CAT_TEST
        }

    def shell_database_example(self, args: tuple):
        arg1, arg2, connection_mode = get_args_from_shell(args)
        print('database_example arg1: {} arg2: {}'.format(arg1, arg2))
        return 'database_example'
