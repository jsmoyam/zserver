from sky_modules.test_module.test_module import TestModule
from sky_modules.acquire_module.acquire_module import AcquireModule
from sky_modules.datasource_module.datasource_module import DatasourceModule
from sky_modules.forensic_module.forensic_module import ForensicModule
from sky_modules.hunting_module.hunting_module import HuntingModule

# This dictionary must be filled when a developer finish a module
module_names = {
    'test_module': TestModule,
    'acquire_module': AcquireModule,
    'datasource_module': DatasourceModule,
    'forensic_module': ForensicModule,
    'hunting_module': HuntingModule,
}


def get_product_modules() -> dict:
    return module_names
