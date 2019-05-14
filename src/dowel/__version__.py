"""Automatically resolve the version of this package."""
import os

# Update this every release to be 'v{next release number}'
NEXT_VERSION = 'v0.0.2'

__version__ = os.environ.get('TRAVIS_TAG', '{}-dev'.format(NEXT_VERSION))
