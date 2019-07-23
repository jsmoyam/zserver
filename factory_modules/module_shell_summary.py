from factory_modules.test_module.shells_test_module import TestModuleShell
from factory_modules.datasource_module.shells_datasource_module import DatasourceModuleShell
from factory_modules.forensic_module.shells_forensic_module import ForensicModuleShell

# This dictionary must be filled when a developer finish a shell module
module_shell_names = {
    'database_object_module': DatasourceModuleShell,
    'test_module': TestModuleShell,
    'forensic_module': ForensicModuleShell,
}

# Categories
CAT_TEST = 'Test'
CAT_FORENSIC = 'Forensic tools'


def get_product_shells() -> list:
    return list(module_shell_names.values())
