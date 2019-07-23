import Pyro4


class TestServer1:
    def __init__(self):
        print('constructor ts1')

    @staticmethod
    def ts1m1(a):
        print('ts1m1: {}'.format(a))
        return 'ts1m1'

    @staticmethod
    def ts1m2(b):
        print('ts1m2: {}'.format(b))
        return 'ts1m2'


class TestServer2:
    def __init__(self):
        print('constructor ts2')

    @staticmethod
    def ts2m1(a):
        print('ts2m1: {}'.format(a))
        return 'ts2m1'

    @staticmethod
    def ts2m2(b):
        print('ts2m2: {}'.format(b))
        return 'ts2m2'

# # Init the pyro-ns
# pyrons = PyroNameServer()
# pyrons.start()


# Expose the TestServer1 class
Pyro4.expose(TestServer1)
# Instance class
obj1 = TestServer1()

# Expose the TestServer2 class
Pyro4.expose(TestServer2)
# Instance class
obj2 = TestServer2()

# Create RPC server
daemon = Pyro4.Daemon(host="127.0.0.1", port=7000)
# Get the pyro4 proxy for a name server
ns = Pyro4.locateNS()

# Register the different classes
uri1 = daemon.register(obj1)
uri2 = daemon.register(obj2)
ns.register("ts1", uri1)
ns.register("ts2", uri2)

# Run the daemon’s request loop to make pyro4 wait for incoming requests
daemon.requestLoop()
