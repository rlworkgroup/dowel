[![Build Status](https://travis-ci.com/rlworkgroup/dowel.svg?branch=master)](https://travis-ci.com/rlworkgroup/dowel)
[![codecov](https://codecov.io/gh/rlworkgroup/dowel/branch/master/graph/badge.svg)](https://codecov.io/gh/rlworkgroup/dowel)
[![Docs](https://readthedocs.org/projects/dowel/badge)](http://dowel.readthedocs.org/en/latest/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/rlworkgroup/dowel/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/dowel.svg)](https://badge.fury.io/py/dowel)

# dowel

dowel is a little logger for machine learning research.

## Installation
```shell
pip install dowel
```

## Usage
```python
import dowel
from dowel import logger, tabular

logger.add_output(dowel.StdOutput())
logger.add_output(dowel.TensorBoardOutput('tensorboard_logdir'))

logger.log('Starting up...')
for i in range(1000):
    logger.push_prefix('itr {}'.format(i))
    logger.log('Running training step')

    tabular.record('itr', i)
    tabular.record('loss', 100.0 / (2 + i))
    logger.log(tabular)

    logger.pop_prefix()
    logger.dump_all()

logger.remove_all()
```
