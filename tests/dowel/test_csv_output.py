import csv
import sys
import tempfile
import unittest
import warnings

from dowel import CsvOutput, TabularInput
from dowel.csv_output import CsvOutputWarning


def patched_assert_warns(self):
    # Stolen from cpython PR#4800. Fixes assertWarns in the presence of modules
    # that import in response to getattr calls.
    # The __warningregistry__'s need to be in a pristine state for tests
    # to work properly.
    for v in list(sys.modules.values()):
        if getattr(v, '__warningregistry__', None):
            v.__warningregistry__ = {}
    self.warnings_manager = warnings.catch_warnings(record=True)
    self.warnings = self.warnings_manager.__enter__()
    warnings.simplefilter('always', self.expected)
    return self


# This is a hack we should undo when cpython#4800 is merged.
unittest.case._AssertWarnsContext.__enter__ = patched_assert_warns


class TestCsvOutput(unittest.TestCase):
    def setUp(self):
        self.log_file = tempfile.NamedTemporaryFile()
        self.csv_output = CsvOutput(self.log_file.name)
        self.tabular = TabularInput()
        self.tabular.clear()

    def tearDown(self):
        self.log_file.close()

    def test_record(self):
        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.tabular.record('bar', bar)
        self.csv_output.record(self.tabular)
        self.tabular.record('foo', foo * 2)
        self.tabular.record('bar', bar * 2)
        self.csv_output.record(self.tabular)
        self.csv_output.dump()

        correct = [
            {'foo': str(foo), 'bar': str(bar)},
            {'foo': str(foo * 2), 'bar': str(bar * 2)},
        ]  # yapf: disable
        self.assert_csv_matches(correct)

    def test_record_inconsistent(self):
        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.csv_output.record(self.tabular)
        self.tabular.record('foo', foo * 2)
        self.tabular.record('bar', bar * 2)

        with self.assertWarns(CsvOutputWarning):
            self.csv_output.record(self.tabular)

        # this should not produce a warning, because we only warn once
        self.csv_output.record(self.tabular)

        self.csv_output.dump()

        correct = [
            {'foo': str(foo)},
            {'foo': str(foo * 2)},
        ]  # yapf: disable
        self.assert_csv_matches(correct)

    def test_empty_record(self):
        self.csv_output.record(self.tabular)
        assert not self.csv_output._writer

        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.tabular.record('bar', bar)
        self.csv_output.record(self.tabular)
        assert not self.csv_output._warned_once

    def test_unacceptable_type(self):
        with self.assertRaises(ValueError):
            self.csv_output.record('foo')

    def test_disable_warnings(self):
        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.csv_output.record(self.tabular)
        self.tabular.record('foo', foo * 2)
        self.tabular.record('bar', bar * 2)

        self.csv_output.disable_warnings()

        # this should not produce a warning, because we disabled warnings
        self.csv_output.record(self.tabular)

    def assert_csv_matches(self, correct):
        """Check the first row of a csv file and compare it to known values."""
        with open(self.log_file.name, 'r') as file:
            reader = csv.DictReader(file)

            for correct_row in correct:
                row = next(reader)
                self.assertDictEqual(row, correct_row)
