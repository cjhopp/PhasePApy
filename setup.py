from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


python_version = sys.version_info
__version__ = "1.1.01"

NUMPY_VERSION = 'numpy >= 1.9.2'


class PyTest(TestCommand, object):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        super(PyTest, self).initialize_options()
        self.pytest_args = []

    def finalize_options(self):
        super(PyTest, self).finalize_options()
        self.test_suite = True
        self.test_args = []

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        exit(pytest.main(self.pytest_args))

# readme = open('README.rst').read()

# doclink = """
# Documentation
# -------------
#
# The full documentation is at http://geoscienceaustralia.github.io/passive
# -seismic
# /."""
# history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='PhasePApy',
    version=__version__,
    # description='Repository for development of software and '
    #             'metadata for passive seismic project',
    # long_description=readme + '\n\n' + doclink + '\n\n' + history,
    # author='Geoscience Australia Passive Seismic Team',
    author_email='',
    url='https://github.com/GeoscienceAustralia/PhasePApy',
    packages=['phasepapy', 'phasepapy.associator', 'phasepapy.phasepicker'],
    dependency_links=['https://github.com/matplotlib/basemap/archive/v1.1.0'
                      '.zip#egg=basemap-1.1.0'],
    package_dir={'PhasePApy': 'phasepapy'},
    include_package_data=True,
    install_requires=[
        NUMPY_VERSION,
        'scipy >= 0.15.1',
        'matplotlib >= 2.0.0',  # need to install inside virtualenv for basemap
        'obspy >= 1.1.0',
        'pillow >= 4.1.1',
        # 'cartopy',
        # 'mpi4py == 2.0.0',
        # 'geographiclib',
    ],
    extras_require={
        'dev': [
            'sphinx',
            'ghp-import',
            'sphinxcontrib-programoutput',
            'tox',
            'pytest-flake8 >= 0.8.1',
            'pytest-mock >= 1.6.0',
            'pytest-cov >= 2.5.1',
            'pytest-regtest >= 0.15.1',
            'flake8-docstrings >= 1.1.0',
            'coverage',
            'codecov',
            'coveralls >= 1.1',
            'pytest >= 3.2'
        ]
    },

    license="See Readme",
    zip_safe=False,
    keywords='Seismic, associator, picker, PhasePicker, '
             'FBpicker, AICDpicker, KTpicker, P and S phases',
    classifiers=[
        'Development Status :: 4 - Beta',
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        # "Programming Language :: Python :: 3.7",
        # add additional supported python versions
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis"
        # add more topics
    ],
    cmdclass={
        'test': PyTest,
    }
)
