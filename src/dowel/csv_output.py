"""A `dowel.logger.LogOutput` for CSV files."""
import csv
import warnings

from dowel import TabularInput
from dowel.simple_outputs import FileOutput
from dowel.utils import colorize


class CsvOutput(FileOutput):
    """CSV file output for logger.

    :param file_name: The file this output should log to.
    """

    def __init__(self, file_name):
        super().__init__(file_name, mode="w+")
        self._writer = None
        self._fieldnames = None
        self._warned_once = set()
        self._disable_warnings = False

    @property
    def types_accepted(self):
        """Accept TabularInput objects only."""
        return (TabularInput, )

    def record(self, data, prefix=''):
        """Log tabular data to CSV."""
        if isinstance(data, TabularInput):
            to_csv = data.as_primitive_dict

            if not to_csv.keys() and not self._writer:
                return

            if not self._writer:
                self._fieldnames = list(to_csv.keys())
                self._writer = csv.DictWriter(
                    self._log_file,
                    fieldnames=self._fieldnames,
                    extrasaction='ignore')
                self._writer.writeheader()

            if set(to_csv.keys()) != set(self._fieldnames):
                self._warn('Inconsistent TabularInput keys detected. '
                           'CsvOutput keys: {}. '
                           'TabularInput keys: {}. '
                           'Newly appeared keys will be appended. '.format(
                               set(self._fieldnames), set(to_csv.keys())))
                merged_fieldnames = list(self._fieldnames)
                
                """find and apply the delta between the keys"""
                for i in to_csv.keys():
                    if i not in self._fieldnames:
                        merged_fieldnames.append(i)

                """update the CSV output writer with new keys"""
                self._fieldnames = merged_fieldnames
                self._writer = csv.DictWriter(
                    self._log_file,
                    fieldnames=self._fieldnames,
                    extrasaction='ignore')
                self._update_header()
                self._warn('Updated CSV keys: {}. '.format(self._fieldnames))

            self._writer.writerow(to_csv)

            for k in to_csv.keys():
                data.mark(k)
        else:
            raise ValueError('Unacceptable type.')

    def _update_header(self):
        """update the header of the target CSV file"""
        self._log_file.flush()
        self._log_file.seek(0, 0)
        content = ''.join(self._log_file.readlines()[2:])
        self._log_file.seek(0, 0)
        self._writer.writeheader()
        self._log_file.write(content)

    def _warn(self, msg):
        """Warns the user using warnings.warn.

        The stacklevel parameter needs to be 3 to ensure the call to logger.log
        is the one printed.
        """
        if not self._disable_warnings and msg not in self._warned_once:
            warnings.warn(
                colorize(msg, 'yellow'), CsvOutputWarning, stacklevel=3)
        self._warned_once.add(msg)
        return msg

    def disable_warnings(self):
        """Disable logger warnings for testing."""
        self._disable_warnings = True


class CsvOutputWarning(UserWarning):
    """Warning class for CsvOutput."""

    pass
