import pytest
import os

TESTS = os.path.dirname(__file__)
DATA = os.path.join(TESTS, 'data')


@pytest.fixture
def data_dir():
    return DATA


@pytest.fixture
def event(data_dir):
    return os.path.join(data_dir, 'ga2017qxlpiu')

