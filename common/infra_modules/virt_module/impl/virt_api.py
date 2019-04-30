import abc

from common.infra_modules.virt_module.model_virt_module import VirtMachineData


class VirtApi:
    """
    Abstract class to define the function header of all the access implementations.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, virt_connection: str):
        """
        Builder method of the class.
        """

        self.virt_connection = virt_connection

    @abc.abstractmethod
    def get_stats_virtual_machine(self, ids_vm: list) -> list:
        """
        Get ram, disk data in virtual machine from virtualization software
        :param id_vm: virtual machine id
        :return: list of VirtMachineData object
        """
        pass

    @abc.abstractmethod
    def get_stats_infrastructure(self) -> VirtMachineData:
        """
        Get ram, disk data in infrastructure
        :return: VirtMachineData object
        """
        pass