import functools
import logging
import time

from threading import Lock


def apply_decorator_for_all_methods(decorator, except_private_internal=True):
    """
    Class decorator to apply a decorator to all methods in a class

    :param decorator: decorator to apply
    :param except_private_internal:
    """

    def wrapper(cls):
        if not except_private_internal:
            methods = cls.__dict__
        else:
            methods = [x for x in cls.__dict__ if not x.startswith('_')]
        for m in methods:
            if callable(getattr(cls, m)):
                setattr(cls, m, decorator(getattr(cls, m)))
        return cls

    return wrapper


def synchronized(lock: Lock):
    """
    Decorator to synchronize different methods with a Lock

    :param lock: Locker
    """

    def wrapper(f):
        def new_function(*args, **kw):
            # Acquire the lock
            lock.acquire()
            try:
                # Execute the method
                return f(*args, **kw)
            finally:
                # After finish the execution method, release the lock
                lock.release()

        return new_function

    return wrapper


class log_function:
    """
    Decorator that allows you to log with a specific logger.
    """

    def __init__(self, logger: logging.Logger = None, level: int = logging.INFO, print_result: bool = True):
        """
        Constructor: Create the logger decorator

        :param logger: logger to print
        :param level: logger's level
        :param print_result:
        """

        self.logger = logger
        self.level = level
        self.print_result = print_result

    def __call__(self, func):
        """
        The wrapper wraps the function and log the entry

        :param func: wrapper function
        """

        @functools.wraps(func)
        def wrapper(*args, **kwds):
            """
            High-order function that act the main function

            :param args: the leftmost positional arguments
            :param kwds: the keyword arguments
            """

            # Control if the first_parameter it's a class parameter
            first_position_variable = 0
            if len(func.__code__.co_varnames) > 0 and func.__code__.co_varnames[0] == 'self':
                first_position_variable = 1

            # Get the arguments
            arg_names = func.__code__.co_varnames[first_position_variable:func.__code__.co_argcount]

            arguments = ', '.join(
                '%s=%r' % entry for entry in list(zip(arg_names, args[first_position_variable:])) + list(kwds.items()))

            # Create the entering message
            entry_message = 'Entering {} {}'.format(func.__name__,
                                                    '' if len(arguments) == 0 else 'with {}'.format(arguments))

            # Get the functions's file function's line
            real_filename = func.__code__.co_filename[func.__code__.co_filename.rfind('/') + 1:]
            real_lineno = func.__code__.co_firstlineno

            # Print the message
            if not self.logger:
                print(entry_message)
            else:
                self.logger.log(self.level, entry_message, extra={'name_override': func.__name__,
                                                                  'file_override': real_filename,
                                                                  'lineno_override': real_lineno})

            # Control the time function
            start = time.perf_counter()
            f_result = func(*args, **kwds)
            elapsed_time = round((time.perf_counter() - start) * 1000, 2)

            # Print the message
            if self.print_result:
                exit_message = 'Exiting ({}ms) {} with [{}]'.format(elapsed_time, func.__name__, f_result)
            else:
                exit_message = 'Exiting ({}ms) {}'.format(elapsed_time, func.__name__)

            if not self.logger:
                print(exit_message)
            else:
                self.logger.log(self.level, exit_message, extra={'name_override': func.__name__,
                                                                 'file_override': real_filename,
                                                                 'lineno_override': real_lineno})

            return f_result

        return wrapper


# Apply synchronized decorator and logging decorator
locker = Lock()
@apply_decorator_for_all_methods(synchronized(locker))
@apply_decorator_for_all_methods(log_function())
class TClass:
    def __init__(self):
        self.a = 1
        self.b = 2
        # Run method in the init to check the synchronized decorator
        self.m1(1)

    def m1(self, a):
        self.a = a
        time.sleep(5)

    def m2(self, b):
        self.b = b


if __name__ == "__main__":
    # Instance class
    t = TClass()

    # Run the m2 method. This execution don't start until the m1 method finish because of the synchronized decorator
    t.m2(2)
