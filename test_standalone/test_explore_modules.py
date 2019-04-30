
import pkgutil
import importlib

# for p in pkgutil.iter_modules():
#     print(p[1])

pkg_dir = 'common'

import sys, inspect
def print_classes():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            print(obj)