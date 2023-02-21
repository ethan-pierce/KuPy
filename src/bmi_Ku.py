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

from Ku import Ku_model

class BmiKuModel:
    """Basic model interface for the Kudryavstev permafrost model."""

    _name = 'Kudryavtsev Permafrost Model'

    _input_var_names = {
        'air_temperature',
        'temperature_amplitude',
        'snow_thickness',
        'snow_density',
        'soil_water_content',
        'frozen_vegetation_height',
        'thawed_vegetation_height',
        'frozen_vegetation_diffusivity',
        'thawed_vegetation_diffusivity'
    }

    _output_var_names = {
        'permafrost_temperature',
        'active_layer_thickness'
    }

    _var_units = {
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
        self._time_units = 'years'

    def initialize(self, config_file: str):
        """Initialize the Kudryavstev permafrost model.
        
        Args:
            config_file: str
                Path to the configuration file.
        """
        self._model = Ku_model()

        # Initialization routines
        self._model.initialize(config_file = config_file)
        self._model.read_input_files()



