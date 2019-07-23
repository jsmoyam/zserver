import configparser
import glob
import logging
import logging.config
import logging.handlers
import os
import logstash
import pathlib
import sys

from common.app_model import AppException, AppErrorCode


class CustomFormatter:
    """
    Custom formatter to solve issues with decorators
    """

    def __init__(self, orig_formatter: logging.Formatter):
        """
        Constructor: Set the original formatter
        :param orig_formatter: logging formatter
        """

        self.orig_formatter = orig_formatter

    def format(self, record: str) -> str:
        """
        Set the correct formatter
        :param record: attribute to control

        :return: Message
        :rtype: msg
        """

        if hasattr(record, 'name_override'):
            record.funcName = record.name_override
        if hasattr(record, 'file_override'):
            record.filename = record.file_override
        if hasattr(record, 'lineno_override'):
            record.lineno = record.lineno_override

        msg = self.orig_formatter.format(record)
        return msg


class AppConfig:
    """
    Class to get the configuration options
    """

    # Configuration file configuration
    CONFIG_FILE = 'config'
    CONFIG_FILE_EXTENSION = '*.ini'
    CONFIG_FILE_FOLDER = 'etc'

    BASE_PATH = os.path.dirname(__file__) + os.sep + '..' + os.sep
    CONFIG_PATH = BASE_PATH + CONFIG_FILE_FOLDER + os.sep
    CONFIG_FILE_FULL_PATH = CONFIG_PATH + CONFIG_FILE

    # Application main configuration
    APP_MAIN_CONFIGURATION = 'app'
    APP_MODULES_SUMMARY = 'modules_summary'
    APP_SHELL_SUMMARY_FILE = 'shell_summary_file'
    APP_FORMATTER = None

    # Logstash configuration
    LOGSTASH_HOST = None
    LOGSTASH_PORT = None
    LOGSTASH_ATTR_HOST = 'logstash_host'
    LOGSTASH_ATTR_PORT = 'logstash_port'

    # Log configuration
    LOG_FOLDER = BASE_PATH + 'log' + os.sep
    LOG_FORMATTER = 'log_formatter'
    LOG_IS_CONSOLE_LOG = 'console_log'
    LOG_FILE_STDOUT = LOG_FOLDER + 'stdout.log'
    LOG_FILE_STDERR = LOG_FOLDER + 'stderr.log'
    LOG_MAX_SIZE = 100 * 1024 * 1024
    LOG_MAX_FILES = 10

    # RPC configuration
    RPC_ACTIVE = 'rpc_active'
    RPC_EXPOSED_HOST = 'exposed_host'
    RPC_EXPOSED_PORT = 'exposed_port'

    # Pyro-ns configuration (required for RPC)
    PYRO_NS_HOST = 'pyro_ns_host'
    PYRO_NS_PORT = 'pyro_ns_port'

    # Api configuration
    API_CONFIGURATION = 'api'
    API_HOST = 'host'
    API_PORT = 'port'
    API_DEBUG = 'debug'
    API_SSL = 'ssl_enabled'
    API_SSL_PRIVATE_KEY = 'ssl_private_key'
    API_SSL_CERT = 'ssl_cert'

    # Common configuration for all modules
    ACTIVE = 'active'
    LOG_LEVEL = 'log_level'
    # RPC configuration for expose the module
    RPC_MODULE_EXPOSED = 'exposed_module'
    RPC_MODULE_EXPOSED_NAME = 'exposed_name'
    # RPC configuration for add an exposed module
    RPC_REMOTE_MODULE = 'remote'
    RPC_CONNECT_EXPOSED_MODULE = 'connect_exposed_module'

    # Sections to exclude from return sections method
    SECTION_TO_EXCLUDE = [APP_MAIN_CONFIGURATION, API_CONFIGURATION]

    def __init__(self):
        """
        Constructor: Read the configuration file
        """

        # Read config files
        self.config = dict()
        all_config_files = self.get_config_files()
        for config_file in all_config_files:
            key = pathlib.Path(config_file).stem
            config_parser = configparser.RawConfigParser()
            config_parser.read(config_file)
            self.config[key] = config_parser

        # Redirect console output to files
        use_console_log = self.is_value_active(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.LOG_IS_CONSOLE_LOG)
        if not use_console_log:
            sys.stdout = open(AppConfig.LOG_FILE_STDOUT, 'w')
            sys.stderr = open(AppConfig.LOG_FILE_STDERR, 'w')

        # Read logstash configuration
        try:
            AppConfig.LOGSTASH_HOST = self.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.LOGSTASH_ATTR_HOST)
            AppConfig.LOGSTASH_PORT = self.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.LOGSTASH_ATTR_PORT)
        except AppException:
            pass

        # Set the formatter for logs
        AppConfig.APP_FORMATTER = self.get_value(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.LOG_FORMATTER)

        # Create LOG_FOLDER if not exist
        if not os.path.exists(AppConfig.LOG_FOLDER):
            os.makedirs(AppConfig.LOG_FOLDER)

        # Dictionary to store all modules logs
        self.logs = dict()

        section_config_file = self.get_sections()
        for section in section_config_file:
            # Recover the log level from this section
            try:
                log_level = self.get_value(section, AppConfig.LOG_LEVEL)
            except Exception:
                log_level = 'DEBUG'

            # Create the logger
            log = self.create_logger(section, log_level)
            self.logs[section] = log

    def get_log(self, logger_name: str) -> logging.log:
        """
        Get the logger from his name passed by parameter

        :param logger_name: Logger's name

        :return: Logger if found
        :rtype: Logger
        """

        if logger_name in self.logs.keys():
            return self.logs[logger_name]
        else:
            raise AppException(AppErrorCode.APP_LOG_NOT_FOUND.formatter(logger_name))

    def create_logger(self, logger_name: str, level: str) -> logging.log:
        """
        Create a new logger

        :param logger_name: Logger's name
        :param level: Logger's level

        :return: Created logger
        :rtype: Logger
        """

        # Create logger and set level
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        # Configure the logger
        logger = self.setup_logger(logger, level, logger_name)

        return logger

    def setup_logger(self, logger: logging.log, level: str, logger_name: str) -> logging.log:
        """
        Setup all the configuration of the logger

        :param logger: Logger to setup
        :param level: Level to set
        :param logger_name: Name to set

        :return: Logger after setup
        :rtype: Logger
        """

        # Create formatter
        original_formatter = logging.Formatter(AppConfig.APP_FORMATTER)
        f = CustomFormatter(original_formatter)

        # Create rotating file handler
        rfh = logging.handlers.RotatingFileHandler('{}/{}.log'.format(AppConfig.LOG_FOLDER, logger_name), 'a',
                                                   AppConfig.LOG_MAX_SIZE, AppConfig.LOG_MAX_FILES)
        rfh.setLevel(level)
        rfh.setFormatter(f)

        # Add handler to the logger
        logger.addHandler(rfh)

        # Create logstash handler
        if AppConfig.LOGSTASH_HOST is not None and AppConfig.LOGSTASH_PORT is not None:
            lh = logstash.TCPLogstashHandler(AppConfig.LOGSTASH_HOST, AppConfig.LOGSTASH_PORT, version=1)

            # Add handler to the logger
            logger.addHandler(lh)

        # Create console handler
        use_console_log = self.is_value_active(AppConfig.APP_MAIN_CONFIGURATION, AppConfig.LOG_IS_CONSOLE_LOG)
        if use_console_log:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(f)

            # Add handler to the logger
            logger.addHandler(ch)

        logger.propagate = 0
        return logger

    def get_sections(self, config_type=CONFIG_FILE, exclude_app: bool = False) -> list:
        """
        Recover the different sections of the configuration file

        :param config_type: configuration file
        :param exclude_app: bool to define if exclude app section

        :return: sections of config
        :rtype: list
        """

        if exclude_app:
            return [e for e in self.config[config_type].sections() if e not in self.SECTION_TO_EXCLUDE]

        return self.config[config_type].sections()

    def get_value(self, section: str, key: str, config_type=CONFIG_FILE) -> str:
        """
        Recover value from section and return it

        :param section: a part of the configuration file
        :param key: key to recover the value
        :param config_type: configuration file

        :return: True if active, False if not active
        :rtype: bool
        """

        try:
            return self.config[config_type][section][key]
        except Exception:
            raise AppException(AppErrorCode.APP_CONF_KEYFILE_ERROR.formatter(key))

    def is_value_active(self, section: str, key: str, config_type=CONFIG_FILE) -> bool:
        """
        Check if a value it's true

        :param section: a part of the configuration file
        :param key: key to recover the value
        :param config_type: configuration file

        :return: True if active, False if not active
        :rtype: bool
        """

        try:
            value = self.config[config_type][section][key]
            return value.lower() == 'true'
        except Exception:
            raise AppException(AppErrorCode.APP_CONF_KEYFILE_ERROR.formatter(key))

    def get_config_files(self) -> list:
        """
        Get all configuration files

        :return: files list
        :rtype: list
        """

        return glob.glob(str(pathlib.Path(self.CONFIG_PATH).resolve()) + os.sep + self.CONFIG_FILE_EXTENSION)
