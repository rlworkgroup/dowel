"""Minimal example of dowel usage.

This example demonstrates how to log a simple progress metric using dowel.

The metric is simultaneously sent to the screen, a CSV files, a text log file
and TensorBoard.
"""
import time

import dowel
from dowel import logger

logger.add_output(dowel.StdOutput())
logger.add_output(dowel.CsvOutput('progress.csv'))
logger.add_output(dowel.TextOutput('progress.txt'))
logger.add_output(dowel.TensorBoardOutput('tensorboard_logdir'))

logger.log('Starting up...')
for i in range(1000):
    logger.push_prefix('itr {}: '.format(i))
    logger.log('Running training step')

    time.sleep(0.01)  # Tensorboard doesn't like output to be too fast.

    logger.logkv('itr', i)
    logger.logkv('loss', 100.0 / (2 + i))

    logger.pop_prefix()
    logger.dump_all()

logger.remove_all()
