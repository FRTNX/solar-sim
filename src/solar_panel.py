from simulator_types import Celcius, Percentage, Watt, KiloWatt, Volt

from environment import Environment


class SolarPanel:
    """A solar panel."""
    
    def __init__(self, params):
        self._id: str = ''
        self._environment: Environment = params['environment']
        self._power_rating: Watt = params['standard_conditions']['power_rating']   # max watts per hour under STC
        self._efficiency: Percentage = params['standard_conditions']['efficiency']
        self._temparature_coefficient: Percentage = params['temp_coefficient']
        self._optimal_temparature: Celcius = params['standard_conditions']['temparature']['value']
        self._current_temparature: Celcius = 0.0
        self._area = params['area']

    def status(self):
        """Return panel status."""
        return {
            'panel_id': self._id,
            'power_output': self._get_power_output(),
            'panel_temparature': self._get_panel_temparature()
        }
        
    def update_temparature(self):
        """Update panel temparature."""
        self._get_panel_temparature()
        
    def _get_power_output(self):
        """Takes solar irradiance and panel temparature as input, returns panel power
        output in watts.
        """
        solar_irradiance = self._environment.solar_irradiance() * self._area
        efficiency = self._calculate_efficiency()
        return (solar_irradiance * efficiency) / 3
        
    def _calculate_efficiency(self):
        """Calculate the panels efficiency based on its temparature."""
        panel_temparature = self._get_panel_temparature()
        if panel_temparature > self._optimal_temparature:
            degrees_above_threshold = panel_temparature - self._optimal_temparature
            temparature_correction_factor = self._temparature_coefficient * degrees_above_threshold
            return self._efficiency - temparature_correction_factor
        else:
            return self._efficiency
        
    def _get_panel_temparature(self):
        """Calculate panel temparature based on environment temparatures and cooling factors."""
        environment_temp = self._environment.temparature
        self._current_temparature = environment_temp - self._cooling_factors()
        return self._current_temparature
        
    def _cooling_factors(self):
        """Returns the temparature drop accounted for by water and air conditioners."""
        return 0      # todo: add appropriate mechanisms

    def json(self):
        """Return json representation of panel."""
        return {
            'panel_id': self._id,
            'power_rating': self._power_rating,
            'efficiency': self._efficiency,
            'temparature_coefficient': self._temparature_coefficient,
            'optimal_temparature': self._optimal_temparature,
            'current_temparature': self._current_temparature,
            'area': self._area
        }


class SolarArray:
    """Creates a single interface to an array of solar panels."""
    
    def __init__(self):
        """Create an empty solar panel array."""
        self._panels = []
        self._array_temparature = 0
        self._total_output = 0
        
    def add(self, panel: SolarPanel):
        """Add a solar panel to the array."""
        self._panels.append(panel)
        return { 'result': 'SUCCESS' }
        
    def remove(self, panel_id: str):
        """Remove a solar panel from the array."""
        for panel in self._panels:
            if panel['_id'] == panel_id:
                self._panels.pop(self._panels.index(panel))
                return { 'result':'SUCCESS' }
        return { 'error': 'PANEL_NOT_FOUND' }
        
    def get_panel_details(self):
        """Return current panel states."""
        panel_details = [panel.status() for panel in self._panels]
        panel_temps = [panel['panel_temparature'] for panel in panel_details]
        self._array_temparature = sum(panel_temps) / len(self._panels)
        self._total_output = sum([panel['power_output'] for panel in panel_details])
        return {
            'array_temparature': self._array_temparature,
            'total_output': self._total_output,
            'panel_details': panel_details
        }
