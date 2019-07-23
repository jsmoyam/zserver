import os
from subprocess import Popen, check_output, STDOUT
import threading
import time
import shutil
import queue
from concurrent.futures import ThreadPoolExecutor

from common import config

from factory_modules.acquire_module import MODULE_NAME
from factory_modules.factory_module import FactoryModule
from factory_modules.acquire_module.views_acquire_module import TestModule3View
from factory_modules.acquire_module.model_acquire_module import AcquireData, AcquireInputData

logger = config.get_log(MODULE_NAME)


class AcquireModule(FactoryModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """
        self.register_url(TestModule3View, '/acquire')
        #self.segment_size = self.module_config.get_value(MODULE_NAME, 'segment_size')
        self.segment_size = '10 GiB'
        self.repository_path = self.module_config.get_value(MODULE_NAME, 'repository_path')
        self.tasks_list = list()
        self.waiting_processes = list()
        self.max_running_tasks = 1
        self.running_tasks = 0


        executor = ThreadPoolExecutor(1)
        executor.submit(self.manage_queue)

    def acquire_efw(self, acquire_data: AcquireData) -> None:
        """
        Acquire a device by its name, using the ewfacquire utility.

        :param acquire_data: An object containing information about the acquisition.
        :type acquire_data AcquireData

        :return: this method return nothing.
        :rtype: None
        """

        # Making the destination folder, and setting the log and images paths.
        dest_folder = os.path.join(self.repository_path, acquire_data.alias)
        try:
            os.mkdir(dest_folder)
        except FileExistsError:
            # TODO: ver como gestionar este fallo
            pass
        acquire_data.path = dest_folder
        log_file_name = "{}.log".format(acquire_data.alias)
        log_file_path = os.path.join(dest_folder, log_file_name)
        image_file_base_path = os.path.join(dest_folder, acquire_data.alias)

        with open(log_file_path, 'w') as output:
            # Starting the ewf acquiring process.
            acquire_process = Popen(
                ["sudo", "ewfacquire", "-u", "-c", "fast", "-t", image_file_base_path, "-S", self.segment_size, "-d",
                 "sha256", acquire_data.device], stdout=output, stderr=STDOUT)

            acquire_data.status = "running"

        while acquire_process.poll() is None:
            # Calculate the progress.
            current_size = AcquireModule.get_size_ewf(dest_folder)
            acquire_data.progress = int((current_size / acquire_data.size) * 100)
            time.sleep(3)

        # If the process exit with fail status: clean the files and exit.
        if acquire_process.poll() != 0:
            acquire_data.status = "failed"
            AcquireModule.clean_acquisition(dest_folder)
            return

        # Extract the info from the log file: status and hashes.
        with open(log_file_path, "r") as output:
            output_text = output.readlines()
            if output_text[-1].find("SUCCESS") != -1:
                sha256_value = output_text[-2].split("\t")[1][:-1]
                md5_value = output_text[-3].split("\t")[2][:-1]
                acquire_data.hash_md5 = md5_value
                acquire_data.hash_sha256 = sha256_value
                acquire_data.status = "acquired"
                acquire_data.progress = 100
                try:
                    os.remove(log_file_path)
                except Exception as err:
                    pass
            else:
                # If the acquisition couldn't be done: clean the files and exit.
                acquire_data.status = "failed"
                AcquireModule.clean_acquisition(dest_folder)

        self.running_tasks = self.running_tasks - 1


    def acquire(self, acquire_input_data: AcquireInputData) -> AcquireData:
        """
        Create an AcquireData object from a input and start the corresponding acquisition method of
        the specified type.

        :param acquire_input_data: An object containing the input data.
        :type acquire_input_data AcquireInputData

        :return: the AcquireData object containing acquisition data..
        :rtype: AcquireData
        """

        # Calculate the size of the block device.
        size = check_output(['sudo', 'blockdev', '--getsize64', '/dev/sdb'])
        size = int(size.strip().decode())

        # Create the AcquireData object and append it to the tasks list.
        acquire_data = AcquireData(acquire_input_data.device, acquire_input_data.method, acquire_input_data.alias)
        acquire_data.size = size  # in bytes
        self.tasks_list.append(acquire_data)

        # Check the acquire type in the input, and start the corresponding method.
        if acquire_input_data.method == 'ewf':
            acquire_process = threading.Thread(target=self.acquire_efw, args=(acquire_data,))
            #acquire_process.start()
            self.waiting_processes.append(acquire_process)

        return acquire_data

    def manage_queue(self) -> None:

        while True:
            if len(self.waiting_processes) != 0 and self.running_tasks < self.max_running_tasks:
                self.running_tasks = self.running_tasks + 1
                task = self.waiting_processes.pop(0)
                task.start()
            time.sleep(1)

    def get_task(self, task_id: str) -> AcquireData:
        """
        Search by id and return a AcquireData object from the tasks list.

        :param task_id: A string representing the id of the task searched.
        :type task_id str

        :return: the AcquireData object searched, or None if not found.
        :rtype: AcquireData
        """
        for task in self.tasks_list:
            if task.id == task_id:
                return task
        return None

    def get_acquired_tasks(self):
        """
        Get a list with all ready tasks.

        :return: List with tasks whose state is READY.
        :rtype: list
        """
        ready_list = list()
        for task in self.tasks_list:
            if task.status == "acquired":
                ready_list.append(task)
        return ready_list

    def update_served_tasks(self, served_tasks):
        """
        Change the status of the served acquisitions, store them in database and
        remove them from the tasks_list.
        :return: None
        """
        for task in served_tasks:
            task.status = "served"
            # TODO: guardarla en BBDD
            self.tasks_list.remove(task)


    @staticmethod
    def get_size_ewf(path):
        """
        Calculate the size of a E01 acquisition.

        :param path: The path of the directory where is the acquisition.
        :type path str

        :return: the AcquireData object searched, or None if not found.
        :rtype: AcquireData
        """
        total_size = 0
        for file in os.listdir(path):
            if not file.endswith('log'):
                total_size = total_size + os.path.getsize(os.path.join(path, file))
        return total_size


    @staticmethod
    def clean_acquisition(path: str) -> None:
        """
        Remove the files of an acquisition.

        :param path: The path of the directory where the acquisition is.
        :type path str

        :return: this method return nothing
        :rtype: None
        """
        try:
            shutil.rmtree(path)
        except Exception as err:
            print("Exception removing {} : {}".format(path, str(err)))

