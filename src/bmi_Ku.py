"""Kudryavtsev permafrost model, adapted from Anisimov et al. (1997).

Anisimov, O. A., Shiklomanov, N. I., & Nelson, F. E. (1997).
Global warming and active-layer thickness: results from transient general circulation models. 
Global and Planetary Change, 15(3-4), 61-77. DOI:10.1016/S0921-8181(97)00009-X

*The MIT License (MIT)*
Copyright (c) 2016 permamodel
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*
"""

import numpy as np
from src.Ku import Ku_model

class BmiKuModel:
    """Basic model interface for the Kudryavstev permafrost model."""

    _name = 'Kudryavtsev Permafrost Model'

    _input_var_names = [
        'air_temperature',
        'temperature_amplitude',
        'snow_thickness',
        'snow_density',
        'soil_water_content',
        'frozen_vegetation_height',
        'thawed_vegetation_height',
        'frozen_vegetation_diffusivity',
        'thawed_vegetation_diffusivity'
    ]

    _output_var_names = [
        'permafrost_temperature',
        'active_layer_thickness'
    ]

    _var_units_map = {
        'air_temperature': 'degrees C',
        'temperature_amplitude': 'degrees C',
        'snow_thickness': 'meters',
        'snow_density': 'kilograms per cubic meter',
        'soil_water_content': 'cubic meters (water) per cubic meter (soil)',
        'frozen_vegetation_height': 'meters',
        'thawed_vegetation_height': 'meters',
        'frozen_vegetation_diffusivity': 'square meters per second',
        'thawed_vegetation_diffusivity': 'square meters per second',
        'permafrost_temperature': 'degrees C',
        'active_layer_thickness': 'meters'
    }

    def __init__(self):
        """Initialize the Basic Model Interface."""
        self._model = None
        self._values = {}
        self._var_units = {}
        self._var_loc = {}
        self._grids = {}
        self._grid_type = {}
        
        self._start_time = 0
        self._end_time = None
        self._current_time = 0

        # Using 'years' as a time unit is generally not preferred
        # However, the Ku model does not support ANY time step other than 1 year
        self._time_units = 'years'

    def initialize(self, config_file: str):
        """Initialize the Kudryavstev permafrost model.
        
        Args:
            config_file: str
                Path to the configuration file.
        """
        self._model = Ku_model()

        # Initialization routines
        self._model.read_config(config_file = config_file)
        self._model.read_input_files()

        self._values = {
            var: getattr(self._model, var).values for var in self._input_var_names
        }
        for var in self._output_var_names:
            self._values[var] = np.empty((
                self._model.number_of_years, 
                self._model.grid_shape[0],
                self._model.grid_shape[1]
            ))

        self._var_units = self._var_units_map.copy()

        self._var_loc = {
            var: 'node' for var in self._input_var_names + self._output_var_names
        }

        self._grids = {
            i: list(self._var_units_map.keys())[i] for i in range(len(self._var_units_map.keys())) 
        }

        self._grid_type = {
            i: 'uniform_rectilinear' for i in range(len(self._var_units_map.keys())) 
        }

        self._start_time = 0
        self._end_time = self._model.number_of_years

    def update(self):
        """Run the model for the current time step."""
        self._model.run_one_step(self._current_time)
        self._current_time += 1

    def update_until(self, end_time: int):
        """Update the model until a certain year (inclusive)."""
        years = self._current_time + end_time

        for t in np.arange(self._current_time, end_time + 1, 1):
            self._model.run_one_step(t)

        self._current_time = end_time

    def finalize(self, path_to_output = None):
        """If specified, write output to a netcdf file."""

        if path_to_output is not None:
            self._model.write_output(path_to_output, vars_to_write = self._output_var_names)

    def get_component_name(self) -> str:
        """Return the name of the component."""
        return self._name

    def get_input_item_count(self) -> int:
        """Return the number of input variables."""
        return len(self._input_var_names)

    def get_output_item_count(self) -> int:
        """Return the number of output variables."""
        return len(self._output_var_names)

    def get_input_var_names(self) -> list:
        """Return a list of input variables."""
        return self._input_var_names
    
    def get_output_var_names(self) -> list:
        """Return a list of output variables."""
        return self._output_var_names

    def get_var_grid(self, var: str) -> int:
        """Return the grid ID for a variable."""
        for grid, variables in self._grids.items():
            if var in variables:
                return grid 

    def get_var_type(self, var: str) -> str:
        """Return the data type of a variable."""
        return str(self.get_value(var).dtype)

    def get_var_units(self, var: str) -> str:
        """Return the units of a variable."""
        return self._var_units[var]

    def get_var_nbytes(self, var: str) -> int:
        """Return the size of a variable in bytes."""
        return self.get_value(var).nbytes

    def get_var_itemsize(self, var: str) -> int:
        """Return the size of one element of a variable in bytes."""
        return np.dtype(self.get_var_type(var)).itemsize

    def get_var_location(self, var: str) -> str:
        """Returns the location of a variable on the grid: either 'node', 'edge', or 'face'."""
        return 'node'

    def get_current_time(self) -> int:
        """Return the current time."""
        return self._current_time

    def get_start_time(self) -> int:
        """Return the start time."""
        return self._start_time

    def get_end_time(self) -> int:
        """Return the end time."""
        return self._end_time

    def get_time_units(self) -> str:
        """Return the time units of the model."""
        return self._time_units

    def get_time_step(self) -> str:
        """Return the model's time step."""
        return 1

    

    
        

