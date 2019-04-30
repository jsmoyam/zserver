import Pyro4
import Pyro4.core
import Pyro4.naming

obj = Pyro4.Proxy("PYRONAME:shell_manager_module")
Pyro4.naming.type_meta(obj)
all_methods = obj._pyroMethods
print(all_methods)
methods = [m for m in all_methods if m.startswith('shell_')]
print(all_methods)
# method_to_call = getattr(obj, methods[1])
# method_to_call()

# print(methods)

# obj.example('333', '444')

# SentinelHL
# 0529 vendorid
# 0001 productid
# 0431 revision