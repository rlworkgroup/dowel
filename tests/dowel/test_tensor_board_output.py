import gc
import tempfile
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
import pytest
import scipy.stats

from dowel import Histogram
from dowel import logger
from dowel import TabularInput
from dowel import TensorBoardOutput
from tests.fixtures import NullOutput

try:
    import tensorflow as tf
except ImportError:
    tf = None
if tf is None:
    pytest.skip('tensorflow not installed', allow_module_level=True)


class TfGraphTestCase:

    def setup_method(self):
        if tf is not None:
            self.graph = tf.Graph()
            self.sess = tf.compat.v1.Session(graph=self.graph)
            self.sess.__enter__()
        logger.add_output(NullOutput())

    def teardown_method(self):
        logger.remove_all()
        if tf is not None:
            if tf.compat.v1.get_default_session() is self.sess:
                self.sess.__exit__(None, None, None)
            self.sess.close()
            # These del are crucial to prevent ENOMEM in the CI
            # b/c TensorFlow does not release memory explicitly
            del self.graph
            del self.sess
        gc.collect()


class TBOutputTest(TfGraphTestCase):

    def setup_method(self):
        super().setup_method()
        self.log_dir = tempfile.TemporaryDirectory()
        self.tabular = TabularInput()
        self.tabular.clear()
        self.tensor_board_output = TensorBoardOutput(self.log_dir.name)

    def teardown_method(self):
        self.tensor_board_output.close()
        self.log_dir.cleanup()
        super().teardown_method()


class TestTensorBoardOutput(TBOutputTest):
    """ Simple test without mocks.

    This makes sure that real file output is still functioning.
    """

    def test_record_scalar(self):
        foo = 5
        bar = 10.0
        self.tabular.record('foo', foo)
        self.tabular.record('bar', bar)
        self.tensor_board_output.record(self.tabular)
        self.tensor_board_output.dump()


class TestTensorBoardOutputMocked(TBOutputTest):
    """ Full test which mocks out TensorboardX. """

    def setup_method(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            super().setup_method()
            self.mock_writer = self.tensor_board_output._writer

    @pytest.mark.skipif(tf is None, reason='tensorflow not found')
    def test_record_graph(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            foo = tf.constant(5)  # noqa: F841
            self.tensor_board_output.record(self.graph)

            assert self.mock_writer.file_writer.add_event.call_count == 1

    def test_record_scalar(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            foo = 5
            bar = 10.0
            self.tabular.record('foo', foo)
            self.tabular.record('bar', bar)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            self.mock_writer.add_scalar.assert_any_call('foo', foo, 0)
            self.mock_writer.add_scalar.assert_any_call('bar', bar, 0)

    def test_record_figure(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            fig = plt.figure()
            ax = fig.gca()
            xs = np.arange(10.0)
            ys = xs**2
            ax.scatter(xs, ys)
            self.tabular.record('baz', fig)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            self.mock_writer.add_figure.assert_called_once_with('baz', fig, 0)

    def test_record_tabular(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            foo = 5
            bar = 10.0
            self.tabular.record('foo', foo)
            self.tabular.record('bar', bar)
            self.tensor_board_output.record(self.tabular, prefix='a/')
            self.tensor_board_output.dump()

            self.mock_writer.add_scalar.assert_any_call('foo', foo, 0)
            self.mock_writer.add_scalar.assert_any_call('bar', bar, 0)

    def test_record_scipy_stats_distribution(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            shape = np.ones((2, 10))
            normal = scipy.stats.norm(loc=0.1 * shape, scale=2.0 * shape)
            gamma = scipy.stats.gamma(a=0.2 * shape)
            poisson = scipy.stats.poisson(mu=0.3 * shape)
            uniform = scipy.stats.randint(high=shape, low=-shape)

            self.tabular.record('Normal', normal)
            self.tabular.record('Gamma', gamma)
            self.tabular.record('Poisson', poisson)
            self.tabular.record('Uniform', uniform)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            assert self.mock_writer.add_histogram.call_count == 4

    def test_record_scipy_stats_multivariate_distribution(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            mvn = scipy.stats.multivariate_normal(mean=np.ones(10),
                                                  cov=2.0 * np.ones(10))

            self.tabular.record('MultivariateNormal', mvn)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            assert self.mock_writer.add_histogram.call_count == 1

    def test_record_histogram(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            norm = scipy.stats.norm(loc=[1., 0.], scale=[0.5, 1.5])
            samples = norm.rvs((10000, 2))
            hist = Histogram(samples)
            self.tabular.record('Samples', hist)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            assert self.mock_writer.add_histogram.call_count == 1

    def test_unknown_tabular_value(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            self.tabular.record('foo', dict())
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()
            # 'foo' should be silently ignored

    def test_unknown_input_type(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            with pytest.raises(ValueError):
                foo = np.zeros((3, 10))
                self.tensor_board_output.record(foo)

    def test_record_tabular_without_tensorflow(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            # Emulate not importing Tensorflow
            self.tensor_board_output._tf = None
            foo = 5
            bar = 10.0
            self.tabular.record('foo', foo)
            self.tabular.record('bar', bar)
            self.tensor_board_output.record(self.tabular, prefix='a/')
            self.tensor_board_output.dump()

            self.mock_writer.add_scalar.assert_any_call('foo', foo, 0)
            self.mock_writer.add_scalar.assert_any_call('bar', bar, 0)

    @pytest.mark.skipif(tf is None, reason='tensorflow not found')
    def test_types_accepted(self):
        assert TabularInput in self.tensor_board_output.types_accepted
        assert tf.Graph in self.tensor_board_output.types_accepted

    def test_types_accepted_without_tensorflow(self):
        # Emulate not importing Tensorflow
        self.tensor_board_output._tf = None
        assert TabularInput in self.tensor_board_output.types_accepted


class TestTensorBoardOutputXAxesMocked(TBOutputTest):
    """Test custom x axes."""

    def setup_method(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            super().setup_method()
            self.mock_writer = self.tensor_board_output._writer

    def test_record_scalar_one_axis(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            self.tensor_board_output._x_axis = 'foo'
            self.tensor_board_output._additional_x_axes = []

            foo = 5
            bar = 10.0
            self.tabular.record('foo', foo)
            self.tabular.record('bar', bar)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            self.mock_writer.add_scalar.assert_any_call('bar', bar, foo)
            assert self.mock_writer.add_scalar.call_count == 1

    def test_record_scalar_two_axes(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            self.tensor_board_output._x_axis = 'foo'
            self.tensor_board_output._additional_x_axes = ['bar']

            foo = 5
            bar = 10.0
            self.tabular.record('foo', foo)
            self.tabular.record('bar', bar)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            self.mock_writer.add_scalar.assert_any_call('foo/bar', foo, bar)
            self.mock_writer.add_scalar.assert_any_call('bar', bar, foo)
            assert self.mock_writer.add_scalar.call_count == 2

    def test_record_scalar_nonexistent_axis(self):
        with mock.patch('tensorboardX.SummaryWriter'):
            self.tensor_board_output._default_step = 0
            self.tensor_board_output._x_axis = 'qux'
            self.tensor_board_output._additional_x_axes = ['bar']

            foo = 5
            bar = 10.0
            self.tabular.record('foo', foo)
            self.tabular.record('bar', bar)
            self.tensor_board_output.record(self.tabular)
            self.tensor_board_output.dump()

            self.mock_writer.add_scalar.assert_any_call('foo', foo, 0)
            self.mock_writer.add_scalar.assert_any_call('bar', bar, 0)
            assert self.mock_writer.add_scalar.call_count == 2
