from simulator_types import Watt, Celcius
from typing import List

from inverter import Inverter
from utils import InsufficientPowerError


class CoolingSystem:
    """Generic cooling system applied to a solar array."""
    
    def __init__(self):
        """Initialise a new cooling system."""
        self._max_output: Celcius = 15
        self._watts_per_degree: Watt = 10
        self._target_temparature: Celcius = 0
        self._current_output: Celcius = 0
        self._power_source: Inverter = None
        self._interval: int = 2
        self._time_series: List[dict] = []
        
    def add_power_source(self, power_source: Inverter):
        """Connect cooling system to power source."""
        self._power_source = power_source
        
    def yield_(self, panel_id):
        """Cool down a target solar panel."""
        try:
            cooling_power = self._watts_per_degree * self._current_output
            power = self._power_source.get_power(cooling_power)
            self._time_series.append({ 'output': self._current_output, 'target': panel_id })
            return self._current_output
        except InsufficientPowerError:
            self._time_series.append({ 'output': 0, 'target': panel_id })
            return 0                                        # no air-conditioning for you
             