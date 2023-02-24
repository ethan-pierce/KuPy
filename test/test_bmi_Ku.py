import pytest
from src.bmi_Ku import BmiKuModel
from numpy.testing import assert_approx_equal, assert_array_equal

def test_always_passes():
    assert True

@pytest.fixture
def Init():
    return BmiKuModel()

def test_bmi_fixture_init(Init):
    assert Init._model == None

def test_bmi_fixture_initialize(Init):
    test_config = './test/config.toml'
    Init.initialize(test_config)

    assert len(Init._values.keys()) == 11

    for var in Init._input_var_names:
        assert Init._values[var].shape == (100, 100, 100)
    for var in Init._output_var_names:
        assert Init._values[var].shape == (100, 100, 100)

    for var in Init._input_var_names:
        assert var in Init._grids.values()
    for var in Init._output_var_names:
        assert var in Init._grids.values()
        
@pytest.fixture
def Bmi():
    test_config = './test/config.toml'
    fixture = BmiKuModel()
    fixture.initialize(test_config)
    return fixture

def test_bmi_update(Bmi):
    Bmi.update()

    assert_approx_equal(Bmi._model.permafrost_temperature[0, 0], -3.006, significant=4)
    assert_approx_equal(Bmi._model.active_layer_thickness[0, 0], 1.226, significant=4)

def test_bmi_update_until(Bmi):
    Bmi.update_until(10)

    assert_approx_equal(Bmi._model.permafrost_temperature[0, 0], -1.7699, significant=4)
    assert_approx_equal(Bmi._model.active_layer_thickness[0, 0], 1.318, significant=4)

def test_get_grid_spacing(Bmi):
    spacing = Bmi.get_grid_spacing(Bmi.get_var_grid('snow_thickness'))
    assert_array_equal(spacing, [1, 1, 1])