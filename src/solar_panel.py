import random

from typing import List, Union
from simulator_types import Celcius, Percentage, Watt

from cooling_system import CoolingSystem
from environment import Environment
from utils import uuid, variation


class SolarPanel:
    """A solar panel."""
    
    def __init__(self, params):
        self._id: str = uuid('PANEL')
        self._environment: Environment = params['environment']
        self._power_rating: Watt = params['standard_conditions']['power_rating']
        self._efficiency: Percentage = params['standard_conditions']['efficiency']
        self._temperature_coefficient: Percentage = params['temp_coefficient']
        self._optimal_temperature: Celcius = params['standard_conditions']['temperature']['value']
        self._current_temperature: Celcius = 0.0
        self._current_output: Watt = 0
        self._area = params['area']
        self._cooling_system: CoolingSystem = CoolingSystem()
        self._time_series = []

    def status(self):   # resolved: called twice as much as pv system and battery
        """Return panel status."""
        self._current_output = self._get_power_output()   # updates temperature, etc
        state = {
            'index': len(self._time_series),
            'panel_id': self._id,
            'power_output': self._current_output,
            'panel_temperature': self._current_temperature
        }
        self._time_series.append(state)
        return state
        
    def _get_power_output(self):
        """Takes solar irradiance and panel temperature as input, returns panel power
        output in watts.
        """
        solar_irradiance = self._environment.solar_irradiance() * self._area
        efficiency = self._calculate_efficiency()
        return variation((solar_irradiance * efficiency) / 3)
        
    def _calculate_efficiency(self):
        """Calculate the panels efficiency based on its temperature."""
        panel_temperature = self._get_panel_temperature()
        if panel_temperature > self._optimal_temperature:
            degrees_above_threshold = panel_temperature - self._optimal_temperature
            temperature_correction_factor = self._temperature_coefficient * degrees_above_threshold
            return self._efficiency - temperature_correction_factor
        else:
            return self._efficiency
        
    def _get_panel_temperature(self):
        """Calculate panel temperature based on environment temperatures and cooling factors."""
        environment_temp = self._environment.temperature
        self._current_temperature = environment_temp - self._cooling_factors()
        return self._current_temperature
        
    def _cooling_factors(self) -> Union[int, float]:
        """Returns the temperature drop accounted for by cooling systems and heat loss."""
        if self._current_temperature > self._optimal_temperature and self._cooling_system._active:
            temperature_difference = self._current_temperature - self._optimal_temperature
            if self._cooling_system._current_output < temperature_difference:
                if self._cooling_system._current_output < self._cooling_system._max_output:
                    self._cooling_system._current_output += 1   # increase cooling system output by 1℃
            else:
                if self._cooling_system._current_output > 0:
                    self._cooling_system._current_output -= 1   # decrease cooling system output by 1℃
            return self._cooling_system.yield_(self._id)
        self._cooling_system.yield_(self._id, reset=True)
        return random.uniform(0, 3)

    def json(self):
        """Return json representation of panel."""
        return {
            'panel_id': self._id,
            'power_rating': self._power_rating,
            'efficiency': self._efficiency,
            'temperature_coefficient': self._temperature_coefficient,
            'optimal_temperature': self._optimal_temperature,
            'current_temperature': self._current_temperature,
            'area': self._area,
            'time_series': self._time_series
        }


class SolarArray:
    """Creates a single interface to an array of solar panels."""
    
    def __init__(self):
        """Create an empty solar panel array."""
        self._id = uuid('SP_ARRAY')
        self._panel_array: List[SolarPanel] = []
        self._array_temperature: Celcius = 0
        self._total_output: Watt = 0
        self._cooling_system = None

    def __iter__(self):
        for panel in self._panel_array:
            yield panel
            
    def __len__(self):
        return len(self._panel_array)
        
    def add(self, panel: SolarPanel):
        """Add a solar panel to the array."""
        self._panel_array.append(panel)
        return { 'result': 'SUCCESS' }
        
    def get(self, panel_id: str):
        """Get target solar panel details."""
        for panel in self._panel_array:
            if panel._id == panel_id:
                return panel.json()
        raise ValueError('PANEL_NOT_FOUND')
    
    def remove(self, panel_id: str):
        """Remove a solar panel from the array."""
        for panel in self._panel_array:
            if panel._id == panel_id:
                panel._cooling_system.yield_(panel._id, reset=True)    # reset cooling system
                self._panel_array.pop(self._panel_array.index(panel))
                return { 'result': 'SUCCESS' }
        raise ValueError('PANEL_NOT_FOUND')
        
    def json(self):
        """Return current panel status."""
        panel_details = [panel.status() for panel in self._panel_array]
        panel_temps = [panel['panel_temperature'] for panel in panel_details]
        self._array_temperature = sum(panel_temps) / len(self._panel_array)
        self._total_output = sum([panel['power_output'] for panel in panel_details])
        return {
            'array_id': self._id,
            'array_temperature': self._array_temperature,
            'total_output': self._total_output,
        }
