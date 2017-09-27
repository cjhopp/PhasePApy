import pytest
import os
import random
import string
from phasepapy.phasepicker import AICDPicker, FBPicker, KTPicker

TESTS = os.path.dirname(__file__)
DATA = os.path.join(TESTS, 'data')


@pytest.fixture
def random_filename(tmpdir_factory):
    def make_random_filename(ext=''):
        dir = str(tmpdir_factory.mktemp('seismic').realpath())
        fname = ''.join(random.choice(string.ascii_lowercase)
                        for _ in range(10))
        return os.path.join(dir, fname + ext)
    return make_random_filename


@pytest.fixture
def data_dir():
    return DATA


@pytest.fixture
def event(data_dir):
    return os.path.join(data_dir, 'ga2017qxlpiu')


@pytest.fixture(params=[AICDPicker, FBPicker, KTPicker])
def picker(request):
    return request.param