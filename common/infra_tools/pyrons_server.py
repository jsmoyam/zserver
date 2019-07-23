import select
import Pyro4.naming
import threading

from common import config
from common.app_config import AppConfig

# Get the app logger
logger = config.get_log(AppConfig.APP_MAIN_CONFIGURATION)


class PyroNameServer(threading.Thread):
    """
    Class to start the pyro4-ns
    """

    def __init__(self):
        """
        Instance the pyro-ns with default configuration
        """

        threading.Thread.__init__(self)
        self._finished = threading.Event()

        self.host = config.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.PYRO_NS_HOST)
        self.port = int(config.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.PYRO_NS_PORT))
        self.server_type = 'thread'

        self.name_server_uri = None
        self.name_server_daemon = None
        self.broadcast_server = None
        self.name_server_sockets = None

    def set_server_type(self, server_type: str):
        """
        Set the server type provided by parameter

        :param server_type: thread=thread pool based, multiplex=select/poll/kqueue based
        """

        self.server_type = server_type

    def set_host(self, host: str):
        """
        Set the host provided by parameter

        :param host: host to deploy the pyro-ns
        """

        self.host = host

    def set_port(self, port: str):
        """
        Set the port provided by parameter

        :param port: port to deploy the pyro-ns
        """

        self.port = port

    def shutdown(self):
        """
        Stop the pyro-ns service
        """

        # Stop pyro-ns
        self.name_server_daemon.close()
        # Stop broadcast server
        if self.broadcast_server:
            self.broadcast_server.close()

        # Stop the thread
        self._finished.set()

    def run(self):

        # Set the configuration server type
        if self.server_type == 'thread':
            Pyro4.config.SERVERTYPE = 'thread'
        elif self.server_type == 'multiplex':
            Pyro4.config.SERVERTYPE = 'multiplex'

        logger.info('INIT PYRONS WITH SERVERTYPE={}'.format(Pyro4.config.SERVERTYPE))

        # Start name server with broadcast server as well
        self.name_server_uri, self.name_server_daemon, self.broadcast_server = Pyro4.naming.startNS(host=self.host,
                                                                                                    port=self.port)

        logger.debug('NS uri: {}'.format(self.name_server_uri))
        logger.debug('NS Daemon location: {}'.format(self.name_server_daemon.locationStr))
        logger.debug('NS Daemon sockets: {}'.format(self.name_server_daemon.sockets))

        logger.info('PYRONS STARTED')

        while True:
            if self._finished.isSet():
                return

            # logger.debug('Waiting for events...')

            # Create sets of the socket objects we will be waiting on
            # (a set provides fast lookup compared to a list)
            self.name_server_sockets = set(self.name_server_daemon.sockets)

            rs = []

            if self.broadcast_server:
                # Only the broadcast server is directly usable as a select() object
                rs.extend(self.broadcast_server)

            rs.extend(self.name_server_sockets)
            rs, _, _ = select.select(rs, [], [], 3)
            events_for_ns = []

            for s in rs:
                if s is self.broadcast_server:
                    # logger.debug('Broadcast server  received a request')
                    self.broadcast_server.processRequest()
                elif s in self.name_server_sockets:
                    # logger.debug('Name server received a request')

                    events_for_ns.append(s)
                    self.name_server_daemon.events(events_for_ns)
