
import gc
import unittest

import tensorflow as tf

from dowel import logger, LogOutput, TabularInput


class NullOutput(LogOutput):
    """Dummy output to disable 'no logger output' warnings."""

    @property
    def types_accepted(self):
        """Accept all output types."""
        return (object, )

    def record(self, data, prefix=''):
        """Don't do anything."""
        if isinstance(data, TabularInput):
            data.mark_all()


class TfGraphTestCase(unittest.TestCase):
    def setUp(self):
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)
        self.sess.__enter__()
        logger.add_output(NullOutput())

    def tearDown(self):
        logger.remove_all()
        if tf.get_default_session() is self.sess:
            self.sess.__exit__(None, None, None)
        self.sess.close()
        # These del are crucial to prevent ENOMEM in the CI
        # b/c TensorFlow does not release memory explicitly
        del self.graph
        del self.sess
        gc.collect()
