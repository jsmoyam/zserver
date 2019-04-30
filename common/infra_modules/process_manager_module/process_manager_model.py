from enum import Enum, unique
from common.infra_modules.process_manager_module import ProcessQueue


@unique
class AlgorithmType(Enum):
    SEQUENTIAL = 1
    PARALLEL = 2
    PRIORITY = 3


@unique
class StatusType(Enum):
    IDLE = 1
    RUNNING = 2
    FINISHED = 3
    FAILED = 4


class Process:

    def __init__(self, process_queue: ProcessQueue) -> None:
        self.id = None
        self.status = StatusType.IDLE
        self.process_queue = process_queue

    def set_id(self, process_id: int) -> None:
        self.id = process_id

    def set_status(self, status: StatusType) -> None:
        self.status = status

    def run(self, process_queue: ProcessQueue) -> object:
        """
        This function must be implemented
        :param process_queue: instance of queue
        :return: data returned by process
        """

        raise NotImplementedError()

    def start(self) -> None:
        """
        Life cycle management
        :return: None
        """

        self.set_status(StatusType.RUNNING)
        try:
            output = self.run(self.process_queue)
            self.process_queue.output[self.id] = output
            self.set_status(StatusType.FINISHED)
        except Exception as e:
            self.process_queue.output[self.id] = e
            self.set_status(StatusType.FAILED)


class ProcessManagerException(Exception):
    """
    Class of standard exception
    """

    def __init__(self, msg: str = '') -> None:
        """
        Constructor with optional message

        :param msg: optional message of the exception
        :type msg: str

        :return: This function return nothing
        :rtype: None
        """

        # Init the father class
        Exception.__init__(self, msg)


class ErrorMessages:
    """
    Class of standard messages of the module
    """

    # Error messages
    LOCKED_QUEUE = 'Queue locked'
    PROCESS_NOT_EXIST = 'Process not exists'
    NOT_OUTPUT_YET = 'Process has not output yet'
