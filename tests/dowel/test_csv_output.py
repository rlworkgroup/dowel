import csv
import tempfile

import pytest

from dowel import CsvOutput
from dowel.csv_output import CsvOutputWarning
from tests.dowel.test_logger import check_misc


class TestCsvOutput:

    def setup_method(self):
        self.log_file = tempfile.NamedTemporaryFile()
        self.csv_output = CsvOutput(self.log_file.name)

    def teardown_method(self):
        self.log_file.close()

    def test_record(self):
        foo = 1
        bar = 10
        self.csv_output.record('foo', foo)
        self.csv_output.record('bar', bar)
        self.csv_output.record('foo', foo * 2)
        self.csv_output.record('bar', bar * 2)
        self.csv_output.dump()

        correct = [
            {'foo': str(foo * 2), 'bar': str(bar * 2)},
        ]  # yapf: disable
        self.assert_csv_matches(correct)

    def test_record_inconsistent(self):
        foo = 1
        bar = 10
        self.csv_output.record('foo', foo)
        self.csv_output.dump()
        self.csv_output.record('foo', foo * 2)
        self.csv_output.record('bar', bar * 2)

        with pytest.warns(CsvOutputWarning):
            self.csv_output.dump()

        # this should not produce a warning, because we only warn once
        self.csv_output.dump()

        correct = [
            {'foo': str(foo)},
            {'foo': str(foo * 2)},
        ]  # yapf: disable
        self.assert_csv_matches(correct)

    def test_empty_record(self):
        self.csv_output.dump()
        assert not self.csv_output._writer

        foo = 1
        bar = 10
        self.csv_output.record('foo', foo)
        self.csv_output.record('bar', bar)
        self.csv_output.dump()
        assert not self.csv_output._warned_once

    def test_disable_warnings(self):
        foo = 1
        bar = 10
        self.csv_output.record('foo', foo)
        self.csv_output.dump()
        self.csv_output.record('foo', foo * 2)
        self.csv_output.record('bar', bar * 2)

        self.csv_output.disable_warnings()

        # this should not produce a warning, because we disabled warnings
        self.csv_output.dump()

    def test_misc(self):
        check_misc(self.csv_output)

    def assert_csv_matches(self, correct):
        """Check the first row of a csv file and compare it to known values."""
        with open(self.log_file.name, 'r') as file:
            reader = csv.DictReader(file)

            for correct_row in correct:
                row = next(reader)
                assert row == correct_row
