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

class TestUpdatePhysicalProperties:

    def test_bulk_heat_capacity(self, Kutest):
        Kutest.update_soil_heat_capacity(0)

        assert_approx_equal(Kutest.bulk_thawed_heat_capacity[0, 0], 1.415e6, significant=4)
        assert_approx_equal(Kutest.bulk_frozen_heat_capacity[0, 0], 1.414e6, significant=4)

    def test_bulk_thermal_conductivity(self, Kutest):
        Kutest.update_soil_thermal_conductivity(0)

        assert_approx_equal(Kutest.bulk_thawed_conductivity[0, 0], 0.5880, significant=4)
        assert_approx_equal(Kutest.bulk_frozen_conductivity[0, 0], 1.0970, significant=4)

    def test_update_snow_thermal_properties(self, Kutest):
        Kutest.update_snow_thermal_properties(0)

        assert_approx_equal(Kutest.snow_thermal_conductivity[0, 0], 0.08182, significant=4)

class TestUpdateSurfaceTemperature:

    def test_update_season_durations(self, Kutest):
        Kutest.update_season_durations(0)

        assert_approx_equal(Kutest.length_of_cold_season[0, 0], 1.951e7, significant=4)
        assert_approx_equal(Kutest.length_of_warm_season[0, 0], 1.205e7, significant=4)

    def test_update_snow_and_veg_insulation(self, Kutest):
        Kutest.update_snow_thermal_properties(0)
        Kutest.update_season_durations(0)
        Kutest.update_ground_surface_temperature(0)

        assert_approx_equal(Kutest.snow_insulation[0, 0], 5.610, significant=4)
        assert_approx_equal(Kutest.snow_damping[0, 0], 3.571, significant=4)
        assert_approx_equal(Kutest.temperature_at_vegetation[0, 0], -1.297, significant=4)
        assert_approx_equal(Kutest.amplitude_at_vegetation[0, 0], 15.48, significant=4)

    def test_update_vegetation_effects(self, Kutest):
        Kutest.update_snow_thermal_properties(0)
        Kutest.update_season_durations(0)
        Kutest.update_ground_surface_temperature(0)

        assert_approx_equal(Kutest.winter_vegetation_effect[0, 0], 0.3051, significant=4)
        assert_approx_equal(Kutest.summer_vegetation_effect[0, 0], 0.4896, significant=4)
        assert_approx_equal(Kutest.vegetation_damping[0, 0], 0.3756, significant=4)
        assert_approx_equal(Kutest.vegetation_insulation[0, 0], 0.2391, significant=4)

class TestUpdatePermafrostTemperature:

    def test_update_permafrost_temperature(self, Kutest):
        Kutest.update_snow_thermal_properties(0)
        Kutest.update_season_durations(0)
        Kutest.update_ground_surface_temperature(0)
        Kutest.update_permafrost_temperature(0)

        assert_approx_equal(Kutest.permafrost_temperature[0, 0], 0.0, significant=4)


        