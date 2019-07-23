from factory_modules.test_module.test_module import TestModule
from factory_modules.acquire_module.acquire_module import AcquireModule
from factory_modules.datasource_module.datasource_module import DatasourceModule
from factory_modules.forensic_module.forensic_module import ForensicModule

# This dictionary must be filled when a developer finish a module
module_names = {
    'test_module': TestModule,
    'acquire_module': AcquireModule,
    'datasource_module': DatasourceModule,
    'forensic_module': ForensicModule,
}


def get_product_modules() -> dict:
    return module_names
