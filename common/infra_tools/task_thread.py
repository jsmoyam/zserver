import threading
import time


class TaskThread(threading.Thread):
    """
    Thread that executes a task every N seconds.
    Also offers execute task only one time (not by default)
    """

    def __init__(self):
        """
        Constructor: Init the thread and configure it
        """

        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = 10.0
        self.only_one = False
        self._lock = threading.Lock()
        self.initial_delay = 0.0

    def set_additional_conf(self):
        """
        This method run only one time before the first execution
        """

        pass

    def set_interval(self, interval):
        """
        Set the number of seconds that thread sleep between executions
        :param interval: seconds
        """

        self._interval = interval
        self.only_one = False

    def set_only_one_execution(self):
        """
        Set only one execution without interval
        """

        self._interval = 0.0
        self.only_one = True

    def set_initial_delay(self, initial_delay):
        """
        Delay first task execution
        :param initial_delay: time to wait
        """

        self.initial_delay = initial_delay

    def shutdown(self):
        """
        Stop the thread
        """

        self._finished.set()

    def before_execute_task(self):
        """
        This method run before the execution task
        """

        pass

    def after_execute_task(self):
        """
        This method run after the execution task
        """

        pass

    def run(self):
        """
        Method that init the thread
        """

        # Initial delay
        time.sleep(self.initial_delay)

        # Set additional configuration
        self.set_additional_conf()

        # Run the task until it finished
        while True:
            # Check if task it's finished
            if self._finished.isSet():
                return

            # Acquire the lock
            self._lock.acquire()

            # Execute before start
            self.before_execute_task()

            # Execute task
            self.task()

            # Execute after task
            self.after_execute_task()

            # Release the lock
            self._lock.release()

            # Sleep for interval or until shutdown
            self._finished.wait(self._interval)

            # If only one execution, exit from method
            if self.only_one:
                break

    def task(self):
        """
        The task done by this thread. It must be override in subclasses
        """

        raise NotImplementedError('Method task must be implemented')
