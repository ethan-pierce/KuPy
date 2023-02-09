import numpy as np
import xarray as xr
import tomli

class Ku_model:

    def __init__(self):
        self.experiment = ""
        self.inputs_dir = ""
        self.outputs_dir = ""
        self.number_of_years = 0
        self.grid_shape = [0, 0]
        self.input_files = {}
        self.constants = {}

        # update_soil_heat_capacity()
        self.bulk_thawed_heat_capacity = None
        self.bulk_frozen_heat_capacity = None

        # update_soil_thermal_conductivity()
        self.bulk_thawed_conductivity = None
        self.bulk_frozen_conductivity = None
    
        # update_snow_thermal_properties()
        self.snow_thermal_conductivity = None
        self.snow_thermal_diffusivity = None

        # update_season_durations()
        self.length_of_cold_season = None 
        self.length_of_warm_season = None 

        # update_ground_surface_temperature()
        self.snow_insulation = None
        self.snow_damping = None
        self.temperature_at_vegetation = None
        self.amplitude_at_vegetation = None
        self.winter_vegetation_effect = None
        self.summer_vegetation_effect = None
        self.vegetation_insulation = None
        self.vegetation_damping = None
        self.ground_surface_temperature = None
        self.ground_surface_amplitude = None

        # update_permafrost_temperature()
        self.permafrost_temperature = None
        self.soil_conductivity = None
        self.soil_heat_capacity = None 

        # update_active_layer()
        self.active_layer_thickness = None 
        self.critical_depth = None
        self.permafrost_amplitude = None 

##############
# Initialize #
##############

    def read_config(self, config_file: str):
        with open(config_file, "rb") as file:
            config = tomli.load(file)

        self.experiment = config['experiment']
        self.inputs_dir = config['directories']['inputs_dir']
        self.outputs_dir = config['directories']['outputs_dir']

        self.number_of_years = config['domain']['number_of_years']
        self.grid_shape = config['domain']['grid_shape']

        self.input_files = {var: ncfile for var, ncfile in config['files'].items()}
        self.soils = {soil: props for soil, props in config['soils'].items()}
        self.constants = {var: val for var, val in config['constants'].items()}

    def read_input_files(self):
        if len(self.input_files) == 0:
            raise ValueError("No input files to read: did you call read_config() first?")

        for key, file in self.input_files.items():
            var = key.replace('_file', '')
            data = xr.open_dataarray(self.inputs_dir + file)

            data = self.broadcast(data)

            setattr(self, var, data)

        for soil, props in self.soils.items():
            if len(props['nc_file']) > 0:
                data = xr.open_dataarray(prop['nc_file'])

                data = self.broadcast(data)

            else:
                data = xr.full_like(self.air_temperature, props['scalar_fraction'])

            self.soils[soil]['fraction'] = data

    def broadcast(self, data: xr.DataArray) -> xr.DataArray:
        if data.shape == (self.number_of_years, self.grid_shape[0], self.grid_shape[1]):
            pass

        elif data.shape == (self.grid_shape[0], self.grid_shape[1]):
            data = data.expand_dims({"time": self.number_of_years}, axis = 0)

        elif data.shape == (self.number_of_years,):
            data = data.expand_dims({"x": self.grid_shape[1], "y": self.grid_shape[0]}, axis = [1, 2])

        elif data.shape == (1,):
            dim_name = str(data.dims[0])
            data = data.expand_dims({"time": self.number_of_years, 
                                        "x": self.grid_shape[1], 
                                        "y": self.grid_shape[0]},
                                        axis = [0, 1, 2])
            data = data.squeeze(dim_name)

        else:
            raise ValueError(var + " data cannot be broadcast to shape " + 
                                str((self.number_of_years, self.grid_shape[0], self.grid_shape[1])))

        return data

##########
# Update #
##########

    def update_soil_heat_capacity(self, t: int):
        total_soil_fraction = np.add.reduce([props['fraction'][t,:,:] for soil, props in self.soils.items()])
        weighted_heat_capacity = np.add.reduce([props['heat_capacity'] * props['fraction'][t,:,:] / total_soil_fraction
                                                for soil, props in self.soils.items()])
        weighted_bulk_density = np.add.reduce([props['bulk_density'] * props['fraction'][t,:,:] / total_soil_fraction
                                               for soil, props in self.soils.items()])
        
        # Anisimov et al. (1997)
        self.bulk_thawed_heat_capacity = (weighted_heat_capacity * weighted_bulk_density + 
                                          4190.0 * self.soil_water_content[t,:,:])

        self.bulk_frozen_heat_capacity = (weighted_heat_capacity * weighted_bulk_density +
                                          2025.0 * self.soil_water_content[t,:,:])

    def update_soil_thermal_conductivity(self, t: int):
        total_soil_fraction = np.add.reduce([props['fraction'][t,:,:] for soil, props in self.soils.items()])
        
        dry_thawed_conductivity = np.multiply.reduce(
            [props['conductivity_thawed_dry']**(props['fraction'][t,:,:] / total_soil_fraction)
             for soil, props in self.soils.items()]
        )

        self.bulk_thawed_conductivity = (
            dry_thawed_conductivity**(1 - self.soil_water_content[t,:,:]) * 0.54**(self.soil_water_content[t,:,:])
        )

        dry_frozen_conductivity = np.multiply.reduce(
            [props['conductivity_frozen_dry']**(props['fraction'][t,:,:] / total_soil_fraction)
             for soil, props in self.soils.items()]
        )

        self.bulk_frozen_conductivity = (
            dry_frozen_conductivity**(1 - self.soil_water_content[t,:,:]) * 
            2.35**(self.soil_water_content[t,:,:] - self.constants['uwc']) *
            0.54**(self.constants['uwc'])
        )

    def update_snow_thermal_properties(self, t: int):

        # Sturm et al. (1997), eq. (4)
        self.snow_thermal_conductivity = (
            0.138 -
            1.01 * (self.snow_density[t,:,:] / 1000) +
            3.233 * (self.snow_density[t,:,:] / 1000)**2
        )

        self.snow_thermal_diffusivity = (
            self.snow_thermal_conductivity / (self.snow_density[t,:,:] * self.constants['snow_heat_capacity'])
        )

    def update_season_durations(self, t: int):
        self.length_of_cold_season = self.constants['sec_per_a'] * (
            0.5 - (1.0 / np.pi) * np.arcsin(self.air_temperature[t,:,:] / self.temperature_amplitude[t,:,:])
        )
        self.length_of_warm_season = self.constants['sec_per_a'] - self.length_of_cold_season

    def update_ground_surface_temperature(self, t: int):

        # Anisimov et al. (1997), eq. (7)
        inner_eq7 = np.exp(
            -1.0 * self.snow_thickness[t,:,:] * 
            np.sqrt(np.pi / (self.constants['sec_per_a'] * self.snow_thermal_diffusivity))
        )
        self.snow_insulation = self.temperature_amplitude[t,:,:] * (1 - inner_eq7)
        self.snow_damping = self.snow_insulation * 2.0 / np.pi
        self.temperature_at_vegetation = self.air_temperature[t,:,:] + self.snow_insulation
        self.amplitude_at_vegetation = self.temperature_amplitude[t,:,:] - self.snow_damping

        # Anisimov et al. (1997), eq. (10)
        inner_eq10 = (
            1.0 - np.exp(
                -1.0 * self.frozen_vegetation_height[t,:,:] *
                np.sqrt(np.pi / (2 * self.frozen_vegetation_diffusivity[t,:,:] * self.length_of_cold_season[:,:]))
            )
        )
        self.winter_vegetation_effect = (self.amplitude_at_vegetation - self.temperature_at_vegetation) * inner_eq10

        # Anisimov et al. (1997), eq. (11)
        inner_eq11 = (
            1.0 - np.exp(
                -1.0 * self.thawed_vegetation_height[t,:,:] *
                np.sqrt(np.pi / (2 * self.thawed_vegetation_diffusivity[t,:,:] * self.length_of_warm_season[:,:]))
            )
        )
        self.summer_vegetation_effect = (self.amplitude_at_vegetation + self.temperature_at_vegetation) * inner_eq11

        self.vegetation_insulation = (
            self.winter_vegetation_effect * self.length_of_cold_season +
            self.summer_vegetation_effect * self.length_of_warm_season
        ) / self.constants['sec_per_a'] * (2.0 / np.pi)

        self.vegetation_damping = (
            self.winter_vegetation_effect * self.length_of_cold_season +
            self.summer_vegetation_effect * self.length_of_warm_season
        ) / self.constants['sec_per_a']

        self.ground_surface_temperature = self.temperature_at_vegetation + self.vegetation_insulation
        self.ground_surface_amplitude = self.amplitude_at_vegetation - self.vegetation_damping

    def update_permafrost_temperature(self, t: int):
        
        # Anisimov et al. (1997), eq. (14)
        first_term_eq14 = (
            0.5 * self.ground_surface_temperature[:, :] * 
            (self.bulk_frozen_conductivity + self.bulk_thawed_conductivity)
        )
        second_term_eq14 = (
            self.ground_surface_amplitude * (self.bulk_thawed_conductivity - self.bulk_frozen_conductivity) / np.pi
        )
        inner_eq14 = (
            self.ground_surface_temperature / self.ground_surface_amplitude *
            np.arcsin(self.ground_surface_temperature / self.ground_surface_amplitude) +
            np.sqrt(1.0 - (np.pi**2 / self.ground_surface_amplitude**2))
        )
        numerator_eq14 = first_term_eq14 + second_term_eq14 * inner_eq14

        self.soil_conductivity = np.where(
            numerator_eq14 > 0.0, 
            self.bulk_thawed_conductivity, 
            self.bulk_frozen_conductivity
        )

        self.soil_heat_capacity = np.where(
            numerator_eq14 > 0.0,
            self.bulk_thawed_heat_capacity,
            self.bulk_frozen_heat_capacity
        )

        self.permafrost_temperature = numerator_eq14 / self.soil_conductivity

    def update_active_layer(self, t: int):

        self.latent_heat = self.constants['latent_heat'] * 1e3 * self.soil_water_content[t,:,:]
        
        # Romanovsky et al. (1997), eq. (4)
        self.permafrost_amplitude = (
            (self.ground_surface_amplitude - np.abs(self.permafrost_temperature)) /
            np.log(
                (self.ground_surface_amplitude + self.latent_heat / (2 * self.soil_heat_capacity)) /
                (np.abs(self.permafrost_temperature) + self.latent_heat / (2 * self.soil_heat_capacity))
            ) -
            self.latent_heat / (2 * self.soil_heat_capacity)
        )

        # Romanovsky et al. (1997), eq. (5)
        self.critical_depth = (
            2 * (self.ground_surface_amplitude - np.abs(self.permafrost_temperature)) *
            np.sqrt(
                (self.soil_conductivity * self.soil_heat_capacity * self.constants['sec_per_a']) / np.pi
            ) /
            (2 * self.permafrost_amplitude * self.soil_heat_capacity + self.latent_heat)
        )

        # Romanovsky et al. (1997), eq. (3)
        self.active_layer_thickness = (
            2 * (self.ground_surface_amplitude - np.abs(self.permafrost_temperature)) *
            np.sqrt(self.soil_conductivity * self.soil_heat_capacity * self.constants['sec_per_a'] / np.pi) +
            (2 * self.permafrost_amplitude * self.soil_heat_capacity * self.critical_depth + 
            self.latent_heat * self.critical_depth) *
            self.latent_heat * np.sqrt(
                (self.soil_conductivity * self.constants['sec_per_a']) /
                (self.soil_heat_capacity * np.pi)
            ) /
            (
                2 * self.permafrost_amplitude * self.soil_heat_capacity * self.critical_depth +
                self.latent_heat * self.critical_depth +
                (2 * self.permafrost_amplitude * self.soil_heat_capacity + self.latent_heat) *
                np.sqrt(
                    (self.soil_conductivity * self.constants['sec_per_a']) /
                    (self.soil_heat_capacity * np.pi)
                )
            )
        ) / (2 * self.permafrost_amplitude * self.soil_heat_capacity + self.latent_heat) 

    def run_one_step(self):
        pass

    def run_all_steps(self):
        pass

############
# Finalize #
############

    def write_output(self):
        pass