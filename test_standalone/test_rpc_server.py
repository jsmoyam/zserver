import Pyro4


class TestServer:
    def __init__(self):
        print('constructor')

    def m1(self, a):
        print('m1: {}'.format(a))
        return 'm1'

    def m2(self, b):
        print('m2: {}'.format(b))
        return 'm2'

ExposedClass = Pyro4.expose(TestServer)
obj = TestServer()


daemon = Pyro4.Daemon(host="127.0.0.1", port=7000)
ns = Pyro4.locateNS()
uri = daemon.register(obj)
ns.register("mytestserver", uri)
daemon.requestLoop()


