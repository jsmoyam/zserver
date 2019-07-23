import subprocess
import time
from common.infra_tools.task_thread import TaskThread

class ExecuteCmdTask(TaskThread):
    def __init__(self, logger, command: str) -> None:
        TaskThread.__init__(self)
        self.logger = logger
        self.command = command

    def task(self):
        self.logger.info('[EXECUTE_CMD_TASK] Running command {}'.format(self.command))

        p = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE)
        p.communicate()

        self.logger.info('[EXECUTE_CMD_TASK] Command {} executed'.format(self.command))
