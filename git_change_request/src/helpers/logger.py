
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from logging import getLogger, Filter, Logger, LogRecord
from logging import config as log_config

import inspect
import os
import errno

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': ''
        },
        'debug': {
            'format': ''
        },
    },
    'filters': {
        'exception': {
            '()': 'git_change_request.src.helpers.logger.LoggerMixin.ExceptionFilter',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': '',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['exception']
        }
    },
    'loggers': {
        'github': {'handlers': ['file'],
                    'level': 'DEBUG',
                    'propagate': False}
    }
}


class LoggerMixin:
    """git-cr logger mixin class.
    This class provides an easy interface for other classes throughout to leverage .
    When the ChangeRequest object is created, this logger will be created also.
    Allowing easy access to the logger as follows:
        cr = ChangeRequest(repo_url=<repo_url>)
        cr.logger.info('PR-41!')
    packages (classes) can either include the logger mixin or create
    their own object.
        class NewChangeRequestImplementation(BaseRequest):
            self.logger.info('New Request Impl!')
    Modules that want to use the logger per function base and not per class,
    can access the logger as follows:
        from logging import getLogger
        LOG = getLogger(__name__)
        LOG.info('git-cr!')
    """

    _DEBUG_LOG_FORMAT = ("%(asctime)s %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    _INFO_LOG_FORMAT = ("%(asctime)s %(levelname)s %(message)s")

    _LOG_LEVELS = {
        'debug': DEBUG,
        'info': INFO,
        'warning': WARNING,
        'error': ERROR,
        'critical': CRITICAL
    }

    @classmethod
    def setup_logger(cls, name: str, file_path: str, log_level: str = 'info'):

        # Setting up handlers
        LOGGING_CONFIG['handlers']['file'].update({'filename': file_path})

        # setup logging formatters
        LOGGING_CONFIG['formatters']['default'].update({'format': cls._INFO_LOG_FORMAT})
        LOGGING_CONFIG['formatters']['debug'].update({'format': cls._DEBUG_LOG_FORMAT})

        if not log_level:
            log_level = 'info' if getLogger('git_change_request').getEffectiveLevel() == 20 else 'debug'

        # Configure the individual logger, name is the logger name provided during creation
        LOGGING_CONFIG['loggers'].update({name: {'handlers': ['file'],
                                                 'level': cls._LOG_LEVELS[log_level],
                                                 'propagate': False}})

        if log_level == 'debug':

            for handler in LOGGING_CONFIG['handlers']:
                LOGGING_CONFIG['handlers'][handler].update({'formatter': 'debug'})
                LOGGING_CONFIG['handlers'][handler].update({'level': cls._LOG_LEVELS[log_level]})

            for logger in LOGGING_CONFIG['loggers']:
                LOGGING_CONFIG['loggers'][logger].update({'level': cls._LOG_LEVELS[log_level]})

            for logger in LOGGING_CONFIG['loggers']:
                LOGGING_CONFIG['loggers'][logger].get('handlers').append('console')

        # Init the logging config
        log_config.dictConfig(LOGGING_CONFIG)

    @classmethod
    def create_logger(cls, name: str, data_folder: str = None, log_level: str = 'info'):
        """Create logger.
        This method will create logger's to be used throughout teflo.
        :param data_folder: name of teflo's data folder
        :type data_folder: str
        :param name: Name for the logger to create.
        :type name: str
        :param log_level: Name for the logger to create.
        :type log_level: str
        """

        # create log directory
        log_dir = os.path.join(data_folder, 'logs')

        try:

            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
        except OSError as ex:
            msg = 'Unable to create %s directory' % log_dir
            if ex.errno == errno.EACCES:
                msg += ', permission defined.'
            else:
                msg += ', %s.' % ex
            raise Exception(msg)

        full_path = os.path.join(log_dir, 'git_change_request.log')

        # setup and initialize LOGGING_CONFIG
        if not log_level:
            log_level = 'info'
        cls.setup_logger(name, full_path, log_level)

    @property
    def logger(self) -> Logger:
        """Returns the default logger object."""
        return getLogger(inspect.getmodule(inspect.stack()[1][0]).__name__)

    class ExceptionFilter(Filter):

        def filter(self, record: LogRecord) -> bool:
            if record.getMessage().find('Traceback') != -1:
                return False
            else:
                return True
