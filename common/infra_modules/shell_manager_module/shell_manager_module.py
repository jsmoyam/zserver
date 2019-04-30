from common import config
from common.module import ShellModule
from common.infra_modules.shell_manager_module import MODULE_NAME
from Pyro4.util import SerializerBase


logger = config.get_log(MODULE_NAME)


def statement_dict_to_class(classname, d):
    # Method that deserialize cmd2.Statement class to tuple of tuple
    return tuple(d['raw-attribute'].split())


# Register method in pyro4 for correct deserialization
SerializerBase.register_dict_to_class("statement", statement_dict_to_class)


class ShellManagerModule(ShellModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """
