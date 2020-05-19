import csv
import tempfile

import pytest

from dowel import CsvOutput, TabularInput
from dowel.csv_output import CsvOutputWarning


class TestCsvOutput:

    def setup_method(self):
        self.log_file = tempfile.NamedTemporaryFile()
        self.csv_output = CsvOutput(self.log_file.name)
        self.tabular = TabularInput()
        self.tabular.clear()

    def teardown_method(self):
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

    @pytest.mark.skip(reason="conflicting functionality (overwritten for this feature)")
    def test_record_inconsistent(self):
        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.csv_output.record(self.tabular)
        self.tabular.record('foo', foo * 2)
        self.tabular.record('bar', bar * 2)

        with pytest.warns(CsvOutputWarning):
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
        with pytest.raises(ValueError):
            self.csv_output.record('foo')

    def test_disable_warnings(self):
        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.csv_output.record(self.tabular)
        self.tabular.record('foo', foo * 2)
        self.tabular.record('bar', bar * 2)

        self.csv_output.disable_warnings()
        self.csv_output.dump()

        # this should not produce a warning, because we disabled warnings
        self.csv_output.record(self.tabular)

    def test_inconsistent_keys(self):
        for i in range(4):
            self.tabular.record('itr', i)
            self.tabular.record('loss', 100.0 / (2 + i))

            # the addition of new data to tabular breaks logging to CSV
            if i > 0:
                self.tabular.record('new_data', i)

            self.csv_output.record(self.tabular)
            self.csv_output.dump()

        correct = [
            {'itr': str(0), 'loss': str(50.0), 'new_data': ''},
            {'itr': str(1), 'loss': str(100.0/3.), 'new_data': str(1)},
            {'itr': str(2), 'loss': str(25.0), 'new_data': str(2)},
            {'itr': str(3), 'loss': str(20.0), 'new_data': str(3)}
        ]
        self.assert_csv_matches(correct)

    def assert_csv_matches(self, correct):
        """Check the first row of a csv file and compare it to known values."""
        with open(self.log_file.name, 'r') as file:
            reader = csv.DictReader(file)

            for correct_row in correct:
                row = next(reader)
                print(row)
                assert row == correct_row
