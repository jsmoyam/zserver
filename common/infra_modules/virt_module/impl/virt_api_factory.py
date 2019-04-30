from common.infra_modules.virt_module.model_virt_module import VirtException, ErrorMessages
from common.infra_modules.virt_module.impl.virt_api import VirtApi
from common.infra_modules.virt_module.impl.virt_vmware import VirtVmware


class VirtApiFactory:
    """
    Class to get any implement
    """

    # Static access to implemented class
    _virt = None

    @staticmethod
    def get_connection(virt_sw: str, virt_connection: str) -> VirtApi:
        """
        Get virtualization implementation

        :param virt_sw: name of implementation software
        :param virt_connection:
        """

        if VirtApiFactory._virt is None:
            VirtApiFactory._virt = VirtApiFactory._implement(virt_sw, virt_connection)
        return VirtApiFactory._virt

    @staticmethod
    def _implement(virt_sw: str, virt_connection: str) -> VirtApi:
        """
        Set implementation

        :param virt_sw: name of implemented software
        """

        if virt_sw == 'vmware':
            return VirtVmware(virt_connection)
        else:
            raise VirtException(ErrorMessages.CONFIGURATION_ERROR)
