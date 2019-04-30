from sky_modules.test_module.shells_test_module import TestModuleShell
from sky_modules.datasource_module.shells_datasource_module import DatasourceModuleShell
from sky_modules.forensic_module.shells_forensic_module import ForensicModuleShell
from sky_modules.hunting_module.shells_hunting_module import HuntingModuleShell

# This dictionary must be filled when a developer finish a shell module
module_shell_names = {
    'database_object_module': DatasourceModuleShell,
    'test_module': TestModuleShell,
    'forensic_module': ForensicModuleShell,
    'hunting_module': HuntingModuleShell,
}

# Categories
CAT_TEST = 'Test'
CAT_FORENSIC = 'Forensic tools'


def get_product_shells() -> list:
    return list(module_shell_names.values())
