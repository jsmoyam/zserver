from common.infra_modules.database_object_module.database_object_module import DatabaseObjectModule
from common.infra_modules.monit_module.monit_module import MonitModule
from common.infra_modules.auth_module.auth_module import AuthModule
from common.infra_modules.tree_module.tree_module import TreeModule
from common.infra_modules.shell_manager_module.shell_manager_module import ShellManagerModule
# from common.infra_modules.bluetooth_module.bluetooth_module import BluetoothModule
from common.infra_modules.system_commands_module.system_commands_module import SystemCommandsModule
from common.infra_modules.virt_module.virt_module import VirtModule
from common.infra_modules.parsing_module.parsing_module import ParsingModule
from common.infra_modules.database_module.database_module import DatabaseModule

# This dictionary must be filled when a developer finish a module
module_infra_names = {
    'database_object_module': DatabaseObjectModule,
    'monit_module': MonitModule,
    'auth_module': AuthModule,
    'tree_module': TreeModule,
    'shell_manager_module': ShellManagerModule,
    # 'bluetooth_module': BluetoothModule,
    'system_commands_module': SystemCommandsModule,
    'virt_module': VirtModule,
    'parsing_module': ParsingModule,
    'database_module': DatabaseModule,
}

def get_infra_modules() -> dict:
    return module_infra_names