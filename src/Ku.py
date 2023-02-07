import numpy as np
import xarray as xr

class Ku_model:

    def __init__(self):
        pass
    
##############
# Initialize #
##############

    def read_inputs(self):
        pass

    def setup_soil_textures(self):
        pass

    def broadcast_scalars(self):
        pass 

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