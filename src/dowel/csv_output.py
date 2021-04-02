"""A `dowel.logger.LogOutput` for CSV files."""
import csv
import warnings

import numpy as np

from dowel.simple_outputs import FileOutput
from dowel.tabular import Tabular
from dowel.utils import colorize


class CsvOutput(FileOutput):
    """CSV file output for logger.

    :param file_name: The file this output should log to.
    :param keys_accepted: Regex for which keys this output should accept.
    """

    def __init__(self, file_name, keys_accepted=r'^\S+$'):
        super().__init__(file_name, keys_accepted=keys_accepted)
        self._writer = None
        self._fieldnames = None
        self._warned_once = set()
        self._disable_warnings = False
        self.tabular = Tabular()

    @property
    def types_accepted(self):
        """Accept str and scalar objects."""
        return (str, ) + np.ScalarType

    def record(self, key, value, prefix=''):
        """Log data to a csv file."""
        self.tabular.record(key, value)

    def dump(self, step=None):
        """Flush data to log file."""
        if self.tabular.empty:
            return

        to_csv = self.tabular.as_primitive_dict

        if not to_csv.keys() and not self._writer:
            return

        if not self._writer:
            self._fieldnames = set(to_csv.keys())
            self._writer = csv.DictWriter(self._log_file,
                                          fieldnames=self._fieldnames,
                                          extrasaction='ignore')
            self._writer.writeheader()

        if to_csv.keys() != self._fieldnames:
            self._warn('Inconsistent Tabular keys detected. '
                       'CsvOutput keys: {}. '
                       'Tabular keys: {}. '
                       'Did you change key sets after your first '
                       'logger.log(Tabular)?'.format(set(self._fieldnames),
                                                     set(to_csv.keys())))

        self._writer.writerow(to_csv)

        self._log_file.flush()
        self.tabular.clear()

    def _warn(self, msg):
        """Warns the user using warnings.warn.

        The stacklevel parameter needs to be 3 to ensure the call to logger.log
        is the one printed.
        """
        if not self._disable_warnings and msg not in self._warned_once:
            warnings.warn(colorize(msg, 'yellow'),
                          CsvOutputWarning,
                          stacklevel=3)
        self._warned_once.add(msg)
        return msg

    def disable_warnings(self):
        """Disable logger warnings for testing."""
        self._disable_warnings = True


class CsvOutputWarning(UserWarning):
    """Warning class for CsvOutput."""

    pass
