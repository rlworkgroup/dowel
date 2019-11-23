"""A `dowel.logger.LogOutput` for tensorboard.

It receives the input data stream from `dowel.logger`, then add them to
tensorboard summary operations through tensorboardX.

Note:
Neither TensorboardX nor TensorBoard supports log parametric
distributions. We add this feature by sampling data from a
`tfp.distributions.Distribution` object.
"""
import functools

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import tensorboardX as tbX
try:
    import tensorflow as tf
except ImportError:
    tf = None

from dowel import Histogram
from dowel import LogOutput
from dowel import LoggerWarning
from dowel import TabularInput


class TensorBoardOutput(LogOutput):
    """
    TensorBoard output for logger.

    :param log_dir(str): The save location of the tensorboard event files.
    :param flush_secs(int): How often, in seconds, to flush the added summaries
    and events to disk.
    """

    def __init__(self,
                 log_dir,
                 x_axes=None,
                 flush_secs=120,
                 histogram_samples=1e3):
        self._writer = tbX.SummaryWriter(log_dir, flush_secs=flush_secs)
        self._x_axes = x_axes
        self._default_step = 0
        self._histogram_samples = int(histogram_samples)
        self._added_graph = False
        self._waiting_for_dump = []
        # Used in tests to emulate Tensorflow not being installed.
        self._tf = tf

    @property
    def types_accepted(self):
        """Return the types that the logger may pass to this output."""
        if self._tf is None:
            return (TabularInput, )
        else:
            return (TabularInput, self._tf.Graph)

    def record(self, data, prefix=''):
        """
        Add data to tensorboard summary.

        :param data: The data to be logged by the output.
        :param prefix(str): A prefix placed before a log entry in text outputs.
        """
        if isinstance(data, TabularInput):
            self._waiting_for_dump.append(
                functools.partial(self._record_tabular, data))
        elif self._tf is not None and isinstance(data, self._tf.Graph):
            self._record_graph(data)
        else:
            raise ValueError('Unacceptable type.')

    def _record_tabular(self, data, step):
        nonexist_axes = set()
        custom_axes = True if self._x_axes else False

        if self._x_axes:
            for axis in self._x_axes:
                if axis not in data.as_dict:
                    nonexist_axes.add(axis)

        custom_axes = custom_axes and not (len(nonexist_axes) == len(
            self._x_axes))

        for key, value in data.as_dict.items():
            if isinstance(value, np.ScalarType) and custom_axes:
                for axis in self._x_axes:
                    if axis not in nonexist_axes and key is not axis:
                        x = data.as_dict[axis]
                        self._record_kv('{}/{}'.format(axis, key), value, x)
            else:
                self._record_kv(key, value, step)
            data.mark(key)

        if len(nonexist_axes) > 0:
            raise NonexistentAxesError(list(nonexist_axes))

    def _record_kv(self, key, value, step):
        if isinstance(value, np.ScalarType):
            self._writer.add_scalar(key, value, step)
        elif isinstance(value, plt.Figure):
            self._writer.add_figure(key, value, step)
        elif isinstance(value, scipy.stats._distn_infrastructure.rv_frozen):
            shape = (self._histogram_samples, ) + value.mean().shape
            self._writer.add_histogram(key, value.rvs(shape), step)
        elif isinstance(value, scipy.stats._multivariate.multi_rv_frozen):
            self._writer.add_histogram(key, value.rvs(self._histogram_samples),
                                       step)
        elif isinstance(value, Histogram):
            self._writer.add_histogram(key, value, step)

    def _record_graph(self, graph):
        graph_def = graph.as_graph_def(add_shapes=True)
        event = tbX.proto.event_pb2.Event(
            graph_def=graph_def.SerializeToString())
        self._writer.file_writer.add_event(event)

    def dump(self, step=None):
        """Flush summary writer to disk."""
        # Log the tabular inputs, now that we have a step
        for p in self._waiting_for_dump:
            p(step or self._default_step)
        self._waiting_for_dump.clear()

        # Flush output files
        for w in self._writer.all_writers.values():
            w.flush()

        self._default_step += 1

    def close(self):
        """Flush all the events to disk and close the file."""
        self._writer.close()


class NonexistentAxesError(LoggerWarning):
    """Raise when the specified x axes do not exist in the tabular.

    Args:
        axes: Name of nonexistent axes.

    """

    def __init__(self, axes):
        self.axes = axes

    def to_string(self):
        return '{} {} exist in the tabular data.'.format(
            ', '.join(self.axes),
            'do not' if len(self.axes) > 1 else 'does not')
