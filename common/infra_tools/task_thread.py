import threading
import time

from common.infra_modules.database_object_module.data_model import ErrorMessages


class TaskThread(threading.Thread):
    """Thread that executes a task every N seconds. Also offers execute task only one time (not by default)"""

    def __init__(self):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = 10.0
        self.only_one = False
        self._lock = threading.Lock()
        self.initial_delay = 0.0

    def set_interval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval
        self.only_one = False

    def set_only_one_execution(self):
        """Set only one task execution, not at interval"""
        self.interval = 0.0
        self.only_one = True

    def set_initial_delay(self, initial_delay):
        """Delay first task execution"""
        self.initial_delay = initial_delay

    def shutdown(self):
        """Stop this thread"""
        self._finished.set()

    def before_execute_task(self):
        """This methods run before execution task"""
        pass

    def after_execute_task(self):
        """This methods run after execution task"""
        pass

    def run(self):
        time.sleep(self.initial_delay)

        while True:
            if self._finished.isSet():
                return

            # Acquire lock
            self._lock.acquire()

            # Execute start
            self.before_execute_task()

            # Execute task
            self.task()

            # Execute finish
            self.after_execute_task()

            # Release lock
            self._lock.release()

            # sleep for interval or until shutdown
            self._finished.wait(self._interval)

            if self.only_one:
                break

    def task(self):
        """The task done by this thread - override in subclasses"""
        raise NotImplementedError(ErrorMessages.REPR_ERROR)
