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
        self.constants = {var: val for var, val in config['constants'].items()}

    def read_input_files(self):
        if len(self.input_files) == 0:
            raise ValueError("No input files to read: did you call read_config() first?")

        for var, file in self.input_files.items():
            data = xr.open_dataarray(file)

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

##########
# Update #
##########

    def update_soil_heat_capacity(self):
        pass

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