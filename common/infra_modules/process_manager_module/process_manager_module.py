from common.infra_modules.infra_module import InfraModule
from common.infra_modules.process_manager_module.process_manager_model import Process, ProcessManagerException, \
    AlgorithmType
from common.infra_modules.process_manager_module.process_queue import  ProcessQueue


class ProcessManagerModule(InfraModule):

    def __init__(self) -> None:
        self.queues = dict()

    def add_queue(self, queue_name: str, algorithm: AlgorithmType = AlgorithmType.SEQUENTIAL) -> None:
        """
        Add queue to the system
        :param queue_name: name of the queue
        :param algorithm: algorithm to execute the process queue
        :return: None or exception if queue already exists
        """

        # Check queue name. Raise exception if exists
        self.check_queue_name(queue_name, exist_mode=True)

        # Store process queue in queues
        self.queues[queue_name] = ProcessQueue(algorithm)

    def del_queue(self, queue_name: str, now: bool = False) -> None:
        """
        Delete queue from the system
        :param queue_name: name of the queue
        :param now: stop pending process or not
        :return: None or exception if queue not exists
        """

        # Check queue name. Raise exception if not exists
        self.check_queue_name(queue_name)

        # Delete process queue
        process_queue = self.queues[queue_name]
        process_queue.delete(now)

    def add_process(self, queue_name: str, process: Process) -> None:
        """
        Add process to the queue
        :param queue_name: name of the queue
        :param process: process to add
        :return: None or exception if queue not exists
        """

        # Check queue name. Raise exception if not exists
        self.check_queue_name(queue_name)

        #  Add to the queue
        self.queues[queue_name].add_process(process)

    def get_output(self, queue_name: str, process_id: int) -> dict:
        """
        Get output from process if finished
        :param queue_name: name of the queue
        :param process_id: process id
        :return: None or exception if queue not exists or result is not avalaible
        """

        # Check queue name. Raise exception if not exists
        self.check_queue_name(queue_name)

        # Get output from process queue
        output = self.queues[queue_name].get_ouput(process_id)
        return output

    def get_cache(self, queue_name: str) -> dict:
        """
        Get cache from process
        :param queue_name: name of the queue
        :return: cache dictionary or exception
        """

        # Check queue name. Raise exception if not exists
        self.check_queue_name(queue_name)

        # Get cache from queue
        cache = self.queues[queue_name].get_cache()
        return cache

    def set_cache(self, queue_name: str, values: dict) -> None:
        """
        Set process cache
        :param queue_name: name of the queue
        :param values: values to cache
        :return: None or exception
        """

        # Check queue name. Raise exception if not exists
        self.check_queue_name(queue_name)

        # Set cache
        self.queues[queue_name].set_cache(values)

    def del_cache(self, queue_name: str, cache_id: str = None):
        """
        Delete positions of cache
        :param queue_name: name of the queue
        :param cache_id: position to delete, all if not set
        :return: None or exception
        """

        # Check queue name. Raise exception if not exists
        self.check_queue_name(queue_name)

        # Delete cache
        self.queues[queue_name].del_cache(cache_id)

    def check_queue_name(self, queue_name: str, exist_mode: bool = False):
        """
        If not exists queue raise exception
        Also delete inactive queues
        :param queue_name: queue name
        :param exist_mode: check if exist queue name or not
        :return: None or exception
        """

        # Get all queues ready for delete
        queues_names_to_delete = [name for name in self.queues.keys() if self.queues[name].is_ready_for_delete]
        for name in queues_names_to_delete:
            del(self.queues[name])

        if exist_mode:
            if queue_name in self.queues.keys():
                raise ProcessManagerException()
        else:
            if queue_name not in self.queues.keys():
                raise ProcessManagerException()
