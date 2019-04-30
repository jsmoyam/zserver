import functools
import logging
import time


class log_function:
    """Logging decorator that allows you to log with a specific logger."""

    def __init__(self, logger: logging.Logger = None, level: int = logging.INFO):
        self.logger = logger
        self.level = level

    def __call__(self, func):
        """
        Returns a wrapper that wraps func.
        The wrapper will log the entry and exit points of the function with logging.INFO level.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwds):

            first_position_variable = 0
            if len(func.__code__.co_varnames) > 0 and func.__code__.co_varnames[0] == 'self':
                first_position_variable = 1

            argnames = func.__code__.co_varnames[first_position_variable:func.__code__.co_argcount]
            arguments = ', '.join(
                '%s=%r' % entry for entry in list(zip(argnames, args[first_position_variable:])) + list(kwds.items()))
            entry_message = 'Entering {} {}'.format(func.__name__,
                                                    '' if len(arguments) == 0 else 'with {}'.format(arguments))

            # func.__code__ contains all data from caller function
            real_filename = func.__code__.co_filename[func.__code__.co_filename.rfind('/') + 1:]
            real_lineno = func.__code__.co_firstlineno

            if not self.logger:
                print(entry_message)
            else:
                self.logger.log(self.level, entry_message, extra={'name_override': func.__name__,
                                                                  'file_override': real_filename,
                                                                  'lineno_override': real_lineno})

            start = time.perf_counter()
            f_result = func(*args, **kwds)
            elapsed_time = round((time.perf_counter() - start) * 1000, 2)

            exit_message = 'Exiting ({}ms) {} with [{}]'.format(elapsed_time, func.__name__, f_result)
            if not self.logger:
                print(exit_message)
            else:
                self.logger.log(self.level, exit_message, extra={'name_override': func.__name__,
                                                                 'file_override': real_filename,
                                                                 'lineno_override': real_lineno})

            return f_result

        return wrapper

def apply_decorator_for_all_methods(decorator):
    def decorate(cls):
        except_private_internal = True
        if not except_private_internal:
            methods = cls.__dict__
        else:
            methods = [x for x in cls.__dict__ if not x.startswith('_')]
        for m in methods:
            if callable(getattr(cls, m)):
                setattr(cls, m, decorator(getattr(cls, m)))
        return cls
    return decorate


# @apply_decorator_for_all_methods(log_function())
class TClass:
    def __init__(self):
        self.a = 1
        self.b = 2

    def m1(self, a):
        self.a = a

    def m2(self, b):
        self.b = b


if __name__ == "__main__":
    t_class = apply_decorator_for_all_methods(TClass)
    t = t_class()

    # t = TClass()
    t.m1(1)
    t.m2(2)