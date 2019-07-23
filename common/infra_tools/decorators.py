import functools
import logging
import signal
import time

from threading import Lock


def apply_decorator_to_a_method(decorator):
    """
    Class decorator to apply a decorator to an method

    :param decorator: decorator to apply
    """

    def wrapper(method):
        method = decorator(method)
        return method

    return wrapper


def apply_decorator_for_all_methods(decorator, except_private_internal=True):
    """
    Class decorator to apply a decorator to all methods in a class

    :param decorator: decorator to apply
    :param except_private_internal: If true, don't apply the decorator to private methods
    """

    def wrapper(cls):
        # Get the method from the class
        if not except_private_internal:
            # All methods
            methods = cls.__dict__
        else:
            # Only private methods
            methods = [x for x in cls.__dict__ if not x.startswith('_')]

        # Set the decorator to the methods
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
        def locker(*args, **kw):
            # Acquire the lock
            lock.acquire()
            try:
                # Execute the method
                return f(*args, **kw)
            finally:
                # After finish the execution method, release the lock
                lock.release()

        return locker

    return wrapper


def dump_args(func):
    """This decorator dumps out the arguments passed to a function before calling it"""

    first_position_variable = 0
    if len(func.__code__.co_varnames) > 0 and func.__code__.co_varnames[0] == 'self':
        first_position_variable = 1

    argnames = func.__code__.co_varnames[first_position_variable:func.__code__.co_argcount]
    fname = func.__name__

    def echo_func(*args, **kwargs):
        print(fname, ':', ', '.join(
            '%s=%r' % entry for entry in list(zip(argnames, args[first_position_variable:])) + list(kwargs.items())
            )
        )
        return func(*args, **kwargs)

    return echo_func


def error_handler_views(exceptions: tuple, cls_result):
    """
    Decorator to handler the exceptions from a ViewModule

    :param exceptions: tuple of exceptions to catch
    :param cls_result: schema to create output

    :return: response result object
    :rtype: str
    """

    def wrapper(f):
        def catch_exceptions(*args, **kw):
            app_module = None
            try:
                # Get the app module
                app_module = args[0].app_module

                # Execute the method
                return f(*args, **kw)

            except exceptions as e:
                return app_module.create_output(cls_result, None, e.error_code.code_http, error=e.error_code)

        return catch_exceptions

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
        def wrapper(*args, **kwargs):
            """
            High-order function that act the main function

            :param args: the leftmost positional arguments
            :param kwargs: the keyword arguments
            """

            # Control if the first_parameter it's a class parameter
            first_position_variable = 0
            if len(func.__code__.co_varnames) > 0 and func.__code__.co_varnames[0] == 'self':
                first_position_variable = 1

            # Get the arguments
            arg_names = func.__code__.co_varnames[first_position_variable:func.__code__.co_argcount]

            arguments = ', '.join(
                '%s=%r' % entry for entry in
                list(zip(arg_names, args[first_position_variable:])) + list(kwargs.items()))

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

            # Control the init time function
            start = time.perf_counter()
            # Execute the function
            f_result = func(*args, **kwargs)
            # Control the finish time function
            elapsed_time = round((time.perf_counter() - start) * 1000, 2)

            # Print the message with the time
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


def timeout(seconds, error_message='Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return functools.wraps(func)(wrapper)

    return decorated
