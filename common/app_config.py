import configparser
import glob
import logging
import logging.config
import logging.handlers
import os
import logstash
import pathlib
import sys

from common.app_model import AppException, GenericErrorMessages


class CustomFormatter:
    """
    Custom formatter to solve issues with decorators
    """

    def __init__(self, orig_formatter):
        self.orig_formatter = orig_formatter

    def format(self, record: str) -> str:
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

    # Application main section
    MAIN_CONFIGURATION = 'app'
    API_CONFIGURATION = 'api'

    # Configuration for app
    APP_PRODUCT_SUMMARY_FILE = 'product_summary_file'
    APP_PRODUCT_SHELL_SUMMARY_FILE = 'product_shell_summary_file'
    APP_HOST_LOGSTASH = None
    APP_PORT_LOGSTASH = None
    APP_FORMATTER = None
    APP_ATTR_HOST_LOGSTASH = 'log_logstash_host'
    APP_ATTR_PORT_LOGSTASH = 'log_logstash_port'
    APP_LOG_FORMATTER = 'log_formatter'
    APP_CONSOLE_LOG = 'console_log'

    # Configuration for logs
    LOG_MAX_SIZE = 104857600
    LOG_MAX_FILES = 10

    # Common configuration attributes for all modules
    ACTIVE = 'active'
    ATTR_LOG_LEVEL = 'log_level'
    RPC_ACTIVE = 'rpc_active'
    EXPOSED = 'exposed'
    EXPOSED_NAME = 'exposed_name'
    EXPOSED_HOST = 'exposed_host'
    EXPOSED_PORT = 'exposed_port'
    RPC_CLIENT_NS_PORT = 'rpc_client_ns_port'
    CONNECT_EXPOSED_MODULE = 'connect_exposed_module'
    REMOTE = 'remote'

    # Configuration for api
    API_HOST = 'host'
    API_PORT = 'port'
    API_SSL = 'ssl'
    API_DEBUG = 'debug'

    # Path configuration of file
    CONFIGURE_FILE = 'config'

    # Common folders
    CONFIG_EXTENSION = '*.ini'
    BASE_PATH = os.path.dirname(__file__) + os.sep + '..' + os.sep
    CONFIG_FOLDER = 'etc'
    CONFIG_PATH = BASE_PATH + CONFIG_FOLDER + os.sep
    CONFIG_FILE_FULL_PATH = CONFIG_PATH + CONFIGURE_FILE
    LOG_FOLDER = BASE_PATH + 'log' + os.sep

    # std files
    FILE_STDOUT = LOG_FOLDER + 'stdout.log'
    FILE_STDERR = LOG_FOLDER + 'stderr.log'

    # Log levels
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    level_to_name = {
        CRITICAL: 'CRITICAL',
        ERROR: 'ERROR',
        WARNING: 'WARNING',
        INFO: 'INFO',
        DEBUG: 'DEBUG',
        NOTSET: 'NOTSET',
    }

    name_to_level = {
        'CRITICAL': CRITICAL,
        'ERROR': ERROR,
        'WARN': WARNING,
        'WARNING': WARNING,
        'INFO': INFO,
        'DEBUG': DEBUG,
        'NOTSET': NOTSET,
    }

    def __init__(self):
        """
        Constructor: read properties file
        """

        # Read config files
        self.config = dict()
        all_config_files = self.get_config_files()
        for config_file in all_config_files:
            key = pathlib.Path(config_file).stem
            config_parser = configparser.RawConfigParser()
            config_parser.read(config_file)
            self.config[key] = config_parser

        # Set formater for logs
        AppConfig.APP_FORMATTER = self.get_value(AppConfig.MAIN_CONFIGURATION, AppConfig.APP_LOG_FORMATTER)

        # Redirect stdout and stderr to files
        use_console_log = self.is_value_active(AppConfig.MAIN_CONFIGURATION, AppConfig.APP_CONSOLE_LOG)
        if not use_console_log:
            sys.stdout = open(AppConfig.FILE_STDOUT, 'w')
            sys.stderr = open(AppConfig.FILE_STDERR, 'w')

        # If not exists logstash configuration, do anything
        try:
            AppConfig.APP_HOST_LOGSTASH  = self.get_value(AppConfig.MAIN_CONFIGURATION, AppConfig.APP_ATTR_HOST_LOGSTASH)
            AppConfig.APP_PORT_LOGSTASH  = self.get_value(AppConfig.MAIN_CONFIGURATION, AppConfig.APP_ATTR_PORT_LOGSTASH)
        except:
            pass

        # If LOG_FOLDER does not exist then create
        if not os.path.exists(AppConfig.LOG_FOLDER):
            os.makedirs(AppConfig.LOG_FOLDER)

        # Dictionary to store all modules logs
        self.logs = dict()

        section_modules = self.get_sections()
        for section_module in section_modules:
            try:
                log_level = self.get_value(section_module, AppConfig.ATTR_LOG_LEVEL)
            except:
                log_level = 'DEBUG'

            log = self.create_logger(section_module, log_level)
            self.logs[section_module] = log

    def get_log(self, logger_name: str) -> logging.log:
        if logger_name in self.logs.keys():
            return self.logs[logger_name]
        else:
            raise AppException(msg=GenericErrorMessages.UNKNOWN_LOG_ERROR)

    def create_logger(self, logger_name: str, level: int) -> logging.log:
        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        # Configure_logger
        logger = self.setup_logger(logger, level, logger_name)

        return logger

    def setup_logger(self, logger: logging.log, level: int, logger_name: str) -> logging.log:
        # Create formatter
        original_formatter = logging.Formatter(AppConfig.APP_FORMATTER)
        f = CustomFormatter(original_formatter)

        # Create rotating file handler
        rfh = logging.handlers.RotatingFileHandler('{}/{}.log'.format(AppConfig.LOG_FOLDER, logger_name), 'a',
                                                   AppConfig.LOG_MAX_SIZE, AppConfig.LOG_MAX_FILES)
        rfh.setLevel(level)
        rfh.setFormatter(f)

        # Create console handler
        use_console_log = self.is_value_active(AppConfig.MAIN_CONFIGURATION, AppConfig.APP_CONSOLE_LOG)
        ch = None
        if use_console_log:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(f)

        # Create logstash handler
        if AppConfig.APP_HOST_LOGSTASH is not None and AppConfig.APP_PORT_LOGSTASH is not None:
            lh = logstash.TCPLogstashHandler(AppConfig.APP_HOST_LOGSTASH, AppConfig.APP_PORT_LOGSTASH, version=1)
            logger.addHandler(lh)

        # Add the handlers to the logger
        logger.addHandler(rfh)
        if ch:
            logger.addHandler(ch)
        logger.propagate = 0
        return logger

    def get_sections(self, config_type=CONFIGURE_FILE) -> list:
        """
        Recover sections of config

        :return: sections of config
        :rtype: list
        """

        return self.config[config_type].sections()

    def get_value(self, section: str, key: str, config_type=CONFIGURE_FILE) -> str:
        """
        Recover value from section

        :param key: key of the value
        :type key: str

        :param section: section
        :type section: str

        :return: value
        :rtype: str
        """

        try:
            return self.config[config_type][section][key]
        except Exception as e:
            raise AppException(msg=GenericErrorMessages.KEYFILE_ERROR)

    def is_value_active(self, section: str, key: str, config_type=CONFIGURE_FILE) -> bool:
        """
        Recover value from section and check if it is true

        :param key: key of the value
        :type key: str

        :param section: section
        :type section: str

        :return: active or not
        :rtype: bool
        """

        try:
            value = self.config[config_type][section][key]
            return value.lower() == 'true'
        except Exception as e:
            raise AppException(msg=GenericErrorMessages.KEYFILE_ERROR)

    def get_config_files(self):
        """Get all config file names"""

        return glob.glob(str(pathlib.Path(self.CONFIG_PATH).resolve()) + os.sep + self.CONFIG_EXTENSION)