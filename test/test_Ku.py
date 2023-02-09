import pytest
from numpy.testing import assert_approx_equal

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
    assert Ku.soils['sand']['heat_capacity'] == 1500
    assert len(Ku.constants) > 0

class TestReadInputs:

    def test_throw_error_if_no_files_list(self, Ku):
        with pytest.raises(ValueError):
            Ku.read_input_files()
    
    def test_read_inputs(self, Ku):
        Ku.read_config("./test/config.toml")
        Ku.read_input_files()

        assert Ku.snow_thickness.shape == (100, 100, 100)
        assert Ku.soils['sand']['fraction'].mean() == 0.25

@pytest.fixture
def Kutest():
    K = Ku_model()
    K.read_config("./test/config.toml")
    K.read_input_files()
    return K

class TestUpdateSoilProperties:

    def test_bulk_heat_capacity(self, Kutest):
        Kutest.update_soil_heat_capacity(0)

        assert_approx_equal(Kutest.bulk_thawed_heat_capacity[0, 0], 1.415e6, significant=4)
        assert_approx_equal(Kutest.bulk_frozen_heat_capacity[0, 0], 1.414e6, significant=4)

    def test_bulk_thermal_diffusivity():
        pass
