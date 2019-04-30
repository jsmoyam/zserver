import Pyro4

# obj = Pyro4.Proxy("PYRONAME:test_module")
# obj.example_method()
# obj.initialize()

obj = Pyro4.Proxy("PYRONAME:mytestserver")
print(obj.m1('hola'))