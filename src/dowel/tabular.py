"""A `dowel.logger` input for tabular (key-value) data."""
import numpy as np
from tabulate import tabulate


class Tabular:
    """This helper class saves key-value pairs and can return a table."""

    def __init__(self):
        self._dict = {}

    def __str__(self):
        """Return a string representation of the table for the logger."""
        return tabulate(
            sorted(self.as_primitive_dict.items(), key=lambda x: x[0]))

    def record(self, key, val):
        """Save key/value entries for the table.

        :param key: String key corresponding to the value.
        :param val: Value that is to be stored in the table.
        """
        self._dict[str(key)] = val

    def clear(self):
        """Clear the tabular."""
        self._dict.clear()

    @property
    def as_primitive_dict(self):
        """Return the dictionary, excluding all nonprimitive types."""
        return {
            key: val
            for key, val in self._dict.items() if np.isscalar(val)
        }

    @property
    def as_dict(self):
        """Return the dictionary of tabular items."""
        return self._dict

    @property
    def empty(self):
        """Return whether or not the tabular is empty."""
        return not bool(self._dict)
