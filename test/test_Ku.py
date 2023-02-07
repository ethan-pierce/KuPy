import pytest
from src.Ku import Ku_model

def test_always_passes():
    assert True

@pytest.fixture
def Ku():
    return Ku_model()

def test_read_inputs(Ku):
    Ku.read_inputs()
