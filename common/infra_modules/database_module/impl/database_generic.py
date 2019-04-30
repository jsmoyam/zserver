import logging

from common.infra_tools.decorators import log_function
from common.infra_modules.database_module import MODULE_NAME
from common.infra_modules.database_module.model_database import DatabaseException, ErrorMessages

logger = logging.getLogger(MODULE_NAME)


class DatabaseGeneric:
    pass
