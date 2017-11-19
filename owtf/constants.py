"""
owtf.constants
~~~~~~~~~~~~~~

Ranking constants used across the framework.
"""

import six

# Maps `int` value of ranks with `string` value.
RANKS = {
    OWTF_UNRANKED: (-1, 'Unranked'),
    OWTF_PASSING: (0, 'Passing'),
    OWTF_INFO: (1, 'Informational'),
    OWTF_LOW: (2, 'Low'),
    OWTF_MEDIUM: (3, 'Medium'),
    OWTF_HIGH: (4, 'High'),
    OWTF_CRITICAL: (5, 'Critical'),
}

MODULE_ROOT = os.path.dirname(__import__('owtf').__file__)
DATA_ROOT = os.path.join(MODULE_ROOT, 'data')


# Logging configuration

LOG_LEVELS = {
    logging.NOTSET: 'sample',
    logging.DEBUG: 'debug',
    logging.INFO: 'info',
    logging.WARNING: 'warning',
    logging.ERROR: 'error',
    logging.FATAL: 'fatal',
}
DEFAULT_LOG_LEVEL = 'error'
DEFAULT_LOGGER_NAME = ''
LOG_LEVELS_MAP = {v: k for k, v in six.iteritems(LOG_LEVELS)}
