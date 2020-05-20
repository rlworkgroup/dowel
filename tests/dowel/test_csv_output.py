import csv
import os
import tempfile

import pytest

from dowel import CsvOutput, TabularInput


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
        assert not os.path.exists('{}.tmp'.format(self.log_file.name))

    def test_key_inconsistent(self):
        for i in range(4):
            self.tabular.record('itr', i)
            self.tabular.record('loss', 100.0 / (2 + i))

            # the addition of new data to tabular breaks logging to CSV
            if i > 0:
                self.tabular.record('x', i)

            if i > 1:
                self.tabular.record('y', i + 1)

            # this should not produce a warning, because we only warn once
            self.csv_output.record(self.tabular)
            self.csv_output.dump()

        correct = [{
            'itr': str(0),
            'loss': str(100.0 / 2.),
            'x': '',
            'y': ''
        }, {
            'itr': str(1),
            'loss': str(100.0 / 3.),
            'x': str(1),
            'y': ''
        }, {
            'itr': str(2),
            'loss': str(100.0 / 4.),
            'x': str(2),
            'y': str(3)
        }, {
            'itr': str(3),
            'loss': str(100.0 / 5.),
            'x': str(3),
            'y': str(4)
        }]
        self.assert_csv_matches(correct)

    def test_empty_record(self):
        self.csv_output.record(self.tabular)
        self.csv_output.dump()

        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.tabular.record('bar', bar)
        self.csv_output.record(self.tabular)
        self.csv_output.dump()
        # Empty lines are not recorded
        self.assert_csv_matches([{'foo': str(foo), 'bar': str(bar)}])

    def test_unacceptable_type(self):
        with pytest.raises(ValueError):
            self.csv_output.record('foo')

    def assert_csv_matches(self, correct):
        """Check the first row of a csv file and compare it to known values."""
        with open(self.log_file.name, 'r') as file:
            contents = list(csv.DictReader(file))
            assert len(contents) == len(correct)

            for row, correct_row in zip(contents, correct):
                assert sorted(list(row.items())) == sorted(
                    list(correct_row.items()))
