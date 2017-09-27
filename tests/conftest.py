import pytest
import os
from phasepapy.phasepicker import AICDPicker, FBPicker, KTPicker

TESTS = os.path.dirname(__file__)
DATA = os.path.join(TESTS, 'data')


@pytest.fixture
def data_dir():
    return DATA


@pytest.fixture
def event(data_dir):
    return os.path.join(data_dir, 'ga2017qxlpiu')


@pytest.fixture(params=[AICDPicker, FBPicker, KTPicker])
def picker(request):
    return request.param