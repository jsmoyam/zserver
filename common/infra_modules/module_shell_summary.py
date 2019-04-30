from common.infra_modules.monit_module.shells_monit_module import MonitModuleShell

# This dictionary must be filled when a developer finish a shell module
module_infra_shell_names = {
    'monit_module': MonitModuleShell,
}

# Categories
CAT_VERSION_MANAGEMENT = 'Version management'

def get_infra_shells() -> list:
    return list(module_infra_shell_names.values())
