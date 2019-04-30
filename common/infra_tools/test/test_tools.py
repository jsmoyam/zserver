import random
import time
from threading import Lock, Thread

from nose.tools import assert_true, raises

from common.infra_tools.decorators import dump_args, synchronized, log_function, timeout
from common.infra_tools.task_thread import TaskThread


class TestTools(object):

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """

    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """

    def setup(self):
        """
        This method is run once before _each_ test method is executed
        """

    def teardown(self):
        """
        This method is run once after _each_ test method is executed
        """

    def test_task_thread(self):
        class TaskExample(TaskThread):
            def task(self):
                delay = random.randrange(0, 5)
                # print('task init delay {}'.format(delay))
                time.sleep(delay)
                # print('task end')

        task = TaskExample()
        task.start()
        time.sleep(5)
        task.shutdown()

        assert_true(True)

    def test_dump_args(self):
        @dump_args
        def f1(a, b, c):
            return a + b + c

        f1(1, 2, 3)
        assert_true(True)

    def test_synchonized(self):
        my_lock = Lock()

        @synchronized(my_lock)
        def critical1(*args):
            delay = random.randrange(0, 3)
            # print('critical1 init delay {}'.format(delay))
            time.sleep(delay)
            # print('critical1 end')

        @synchronized(my_lock)
        def critical2(*args):
            delay = random.randrange(0, 3)
            delay = 10
            # print('critical2 init delay {}'.format(delay))
            time.sleep(delay)
            # print('critical2 end')

        t1 = Thread(target=critical1, args=[])
        t2 = Thread(target=critical2, args=[])
        t1.start()
        t2.start()

        my_lock.release()



        assert_true(True)

    def test_log(self):
        @log_function()
        def f1(a):
            pass

        f1(3)

        @log_function()
        def f2():
            pass

        f2()

        assert_true(True)

    @raises(TimeoutError)
    def test_timeout_1(self):
        @timeout(1)
        def f():
            time.sleep(2)

        f()

    def test_timeout_2(self):
        @timeout(2)
        def f():
            time.sleep(1)

        f()
        assert_true(True)
