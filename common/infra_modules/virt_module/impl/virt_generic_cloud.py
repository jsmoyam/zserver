import logging

from common.infra_tools.decorators import log_function
from common.infra_modules.virt_module import MODULE_NAME
from common.infra_modules.virt_module.model_virt_module import VirtException, ErrorMessages

logger = logging.getLogger(MODULE_NAME)


class VirtGenericCloud:
    pass
