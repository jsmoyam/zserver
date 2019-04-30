import logging
import requests
import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import ssl
import re

from common.infra_tools.decorators import log_function
from common.infra_modules.virt_module import MODULE_NAME
from common.infra_modules.virt_module.model_virt_module import VirtMachineData, VirtException, VirtInfraData, ErrorMessages
from common.infra_modules.virt_module.impl.virt_api import VirtApi


logger = logging.getLogger(MODULE_NAME)


class VirtVmware(VirtApi):
    """
    Class to define the specific implementation of Vmware
    """

    def __init__(self, virt_connection: str):
        """
        Constructor with connection string

        :param virt_connection: url connection from ini file
        :return: This function return nothing
        """

        # Init the father class
        VirtApi.__init__(self, virt_connection)

        match_obj = re.match(r'\w+:\/\/(.+):(.+)@(.+):(\d+)', virt_connection)

        self.virt_user = match_obj.group(1)
        self.virt_pass = match_obj.group(2)
        self.virt_host =  match_obj.group(3)
        self.virt_port =  match_obj.group(4)

        try:
            # Connect with vmware
            self.api = self.open_connection()

        except VirtException as e:
            raise e

    @log_function(logger, logging.DEBUG)
    def get_stats_virtual_machine(self, ids_vm: list) -> list:
        """
        Get information from a given list of virtual machines
        :param ids_vms: virtual machine id's list
        :return: list of VirtMachineData object
        """
        result = list()

        # Open the connection and get the content filtering only the virtual machine objects
        si = self.open_connection()
        content = si.RetrieveContent()
        obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.VirtualMachine], True)
        vm_list = obj_view.view

        # Iterate over all the ids given as parameter.
        for id in ids_vm:
            found = False
            # Iterate over all the virtual machines in vCenter
            for vm in vm_list:
                # If it's found, extract the information and add it to the result.
                if id == vm.summary.config.name:
                    result.append(VirtVmware.extract_info_from_vm(vm))
                    found = True
                    break
            # If the id is not found, add None to the result. ??
            if not found:
                result.append(None)
        return result

    def get_stats_infrastructure(self) -> VirtMachineData:
        """
        Get ram, disk data and cpu in infrastructure
        :return: VirtMachineData object
        """
        # Open the connection and get the content filtering only the Host objects
        si = self.open_connection()
        content = si.RetrieveContent()
        hosts = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        hosts_list = hosts.view

        # Initialize the counters
        memory_total = memory_used = cpu_used = cpu_total = disk_total = free_space = 0

        # Iterate over al the host to acummulate the cpu total/used and the memory total/used.
        for host in hosts_list:
            memory_total += host.hardware.memorySize
            memory_used += host.summary.quickStats.overallMemoryUsage
            cpu_total += host.hardware.cpuInfo.hz * host.hardware.cpuInfo.numCpuCores
            cpu_used += host.summary.quickStats.overallCpuUsage

        # Iterate over all the datancenter in the lab.
        for datacenter in content.rootFolder.childEntity:
            datastores = datacenter.datastore
            # Iterate over all the datastore in the datacenter to acummulate the disk total/free
            for ds in datastores:
                disk_total += ds.summary.capacity
                free_space += ds.summary.freeSpace
        # Calculate the used disk.
        disk_used = disk_total - free_space

        # Create a VirtInfraData and populate it with the obtained information
        infra_data = VirtInfraData()
        infra_data.memory_total = memory_total
        infra_data.memory_used = memory_used * 1024 * 1024
        infra_data.cpu_total = cpu_total
        infra_data.cpu_used = cpu_used * 1024 * 1024
        infra_data.disk_total = disk_total
        infra_data.disk_used = disk_used

        return infra_data

    def open_connection(self) :
        """
        Get the connection with Vmware.

        :return: object that represents the connection
        """

        """
           Create vCenter conections

           :param print: Nebula logging system
           """

        # Disable ssl warnings
        requests.packages.urllib3.disable_warnings()
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        si = None
        try:
            # Try to connect to vCenter with the parameters obtained from configuration
            si = SmartConnect(host=self.virt_host,
                              user=self.virt_user,
                              pwd=self.virt_pass,
                              port=self.virt_port)

        except Exception as e:
            logger.error("Exception connecting ")

        if not si:
            return False

        atexit.register(Disconnect, si)
        return si

    # Helper methods

    def get_vm_info_from_name(self, vm_name):

        content = self.api.RetrieveContent()
        obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.VirtualMachine], True)
        vm_list = obj_view.view

        for vm in vm_list:
            if vm_name == vm.summary.config.name:
                return VirtVmware.extract_info_from_vm(vm)
        return None

    @staticmethod
    def extract_info_from_vm(vm):
        vm_obj = VirtMachineData()

        vm_obj.disk_commited = vm.summary.storage.committed
        vm_obj.ram_assigned = vm.summary.config.memorySizeMB * 1024 * 1024
        vm_obj.ram_usage = vm.summary.quickStats.guestMemoryUsage
        vm_obj.cpu_usage = vm.summary.quickStats.overallCpuUsage
        vm_obj.name = vm.summary.config.name

        vm_obj.disks = list()

        for disk in vm.guest.disk:
            new_disk = dict()
            new_disk['path'] = disk.diskPath
            new_disk['capacity'] = disk.capacity
            new_disk['freeSpace'] = disk.freeSpace

            vm_obj.disks.append(new_disk)


            vm_obj
        return vm_obj