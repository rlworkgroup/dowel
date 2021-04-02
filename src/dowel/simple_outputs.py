"""Contains the output classes for the logger.

Each class is sent logger data and handles it itself.
"""
import abc
import datetime
import os
import sys

import dateutil.tz
import numpy as np

from dowel import LogOutput
from dowel.tabular import Tabular
from dowel.utils import mkdir_p


class StdOutput(LogOutput):
    """Standard console output for the logger.

    :param keys_accepted: Regex for which keys this output should accept.
    :param with_timestamp: Whether to log a timestamp before non-tabular data.
    """

    def __init__(self, keys_accepted=r'^', with_timestamp=True):
        super().__init__(keys_accepted=keys_accepted)
        self._with_timestamp = with_timestamp
        self.tabular = Tabular()

    @property
    def types_accepted(self):
        """Accept str and scalar objects."""
        return (str, ) + np.ScalarType

    def record(self, key, value, prefix=''):
        """Log data to console."""
        if not key:
            if isinstance(value, str):
                out = prefix + value
                if self._with_timestamp:
                    now = datetime.datetime.now(dateutil.tz.tzlocal())
                    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                    out = '%s | %s' % (timestamp, out)
                print(out)
            else:
                raise ValueError('Unacceptable type')
        else:
            self.tabular.record(key, value)

    def dump(self, step=None):
        """Flush data to standard output stream."""
        if not self.tabular.empty:
            print(str(self.tabular))
            self.tabular.clear()
        sys.stdout.flush()


class FileOutput(LogOutput, metaclass=abc.ABCMeta):
    """File output abstract class for logger.

    :param file_name: The file this output should log to.
    :param keys_accepted: Regex for which keys this output should accept.
    :param mode: File open mode ('a', 'w', etc).
    """

    def __init__(self, file_name, keys_accepted=r'^', mode='w'):
        super().__init__(keys_accepted=keys_accepted)
        mkdir_p(os.path.dirname(file_name))
        # Open the log file in child class
        self._log_file = open(file_name, mode)

    def close(self):
        """Close any files used by the output."""
        if self._log_file and not self._log_file.closed:
            self._log_file.close()

    def dump(self, step=None):
        """Flush data to log file."""
        self._log_file.flush()


class TextOutput(FileOutput):
    """Text file output for logger.

    :param file_name: The file this output should log to.
    :param keys_accepted: Regex for which keys this output should accept.
    :param with_timestamp: Whether to log a timestamp before the data.
    """

    def __init__(self, file_name, keys_accepted=r'^', with_timestamp=True):
        super().__init__(file_name, keys_accepted=keys_accepted, mode='a')
        self._with_timestamp = with_timestamp
        self.tabular = Tabular()

    @property
    def types_accepted(self):
        """Accept str and scalar objects."""
        return (str, ) + np.ScalarType

    def record(self, key, value, prefix=''):
        """Log data to text file."""
        if not key:
            if isinstance(value, str):
                out = prefix + value
                if self._with_timestamp:
                    now = datetime.datetime.now(dateutil.tz.tzlocal())
                    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
                    out = '%s | %s' % (timestamp, out)
                self._log_file.write(out + '\n')
            else:
                raise ValueError('Unacceptable type')
        else:
            self.tabular.record(key, value)

    def dump(self, step=None):
        """Flush data to log file."""
        if not self.tabular.empty:
            self._log_file.write(str(self.tabular) + '\n')
            self.tabular.clear()
        self._log_file.flush()
