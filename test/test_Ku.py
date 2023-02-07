import pytest
from src.Ku import Ku_model

def test_always_passes():
    assert True

@pytest.fixture
def Ku():
    return Ku_model()

def test_read_config(Ku):
    Ku.read_config("./test/config.toml")
    
    assert Ku.experiment == 'test'
    assert Ku.inputs_dir == './test/data/inputs/'
    assert Ku.outputs_dir == './test/data/outputs/'
    assert Ku.number_of_years == 100
    assert Ku.grid_shape == [100, 100]
    assert len(Ku.input_files) > 0
    assert len(Ku.constants) > 0

class TestReadInputs:

    def test_throw_error_if_no_files_list(self, Ku):
        with pytest.raises(ValueError):
            Ku.read_input_files()
    
    def test_read_inputs(self, Ku):
        Ku.read_config("./test/config.toml")
        Ku.read_input_files()
