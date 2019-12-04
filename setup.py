"""dowel setuptools script."""
from setuptools import find_packages
from setuptools import setup

# Required dependencies
required = [
    # Please keep alphabetized
    'matplotlib',
    'numpy',
    'python-dateutil',
    'scipy',
    'tabulate',
    'tensorboardX',
]

extras = dict()

extras['tensorflow'] = ['tensorflow']

extras['all'] = list(set(sum(extras.values(), [])))

# Development dependencies (*not* included in "all")
extras['dev'] = [
    # Please keep alphabetized
    'coverage',
    'flake8',
    'flake8-docstrings>=1.5.0',
    'flake8-import-order',
    'pep8-naming',
    'pre-commit',
    'pycodestyle>=2.5.0',
    'pydocstyle>=4.0.0',
    'pylint',
    'pytest>=4.4.0',  # Required for pytest-xdist
    'pytest-cov',
    'pytest-xdist',
    'sphinx',
    'recommonmark',
    'yapf',
]

with open('README.md') as f:
    readme = f.read()

with open('VERSION') as v:
    version = v.read().strip()

setup(
    name='dowel',
    version=version,
    author='Reinforcement Learning Working Group',
    author_email='dowel@noreply.github.com',
    description='A logger for machine learning research',
    url='https://github.com/rlworkgroup/dowel',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.5',
    install_requires=required,
    extras_require=extras,
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries',
    ],
)
