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
        self.bulk_thawed_heat_capacity = 0
        self.bulk_frozen_heat_capacity = 0
    
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
                                          4190.0 * self.soil_water_content.values[t,:,:])

        self.bulk_frozen_heat_capacity = (weighted_heat_capacity * weighted_bulk_density +
                                          2025.0 * self.soil_water_content.values[t,:,:])

    def update_soil_thermal_conductivity(self):
        pass

    def update_snow_thermal_properties(self):
        pass

    def update_temperature(self):
        pass

    def update_active_layer(self):
        pass

    def run_one_step(self):
        pass

    def run_all_steps(self):
        pass

############
# Finalize #
############

    def write_output(self):
        pass