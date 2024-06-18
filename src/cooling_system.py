from simulator_types import Watt, Celcius
from typing import List

from inverter import Inverter
from utils import InsufficientPowerError, uuid


class CoolingSystem:
    """Generic cooling system applied to a solar array."""
    
    def __init__(self):
        """Initialise a new cooling system."""
        self._id: str = uuid('COOLING')
        self._max_output: Celcius = 15
        self._watts_per_degree: Watt = 15
        self._target_temparature: Celcius = 0
        self._current_output: Celcius = 0                   # controlled by corresponding solar panel
        self._power_source: Inverter = None
        self._active: bool = True
        self._time_series: List[dict] = []
        
    def start(self):
        self._active = True
        
    def stop(self):
        self._active = False
        
    def add_power_source(self, power_source: Inverter):
        """Connect cooling system to power source."""
        self._power_source = power_source
        
    def yield_(self, panel_id: str, reset: bool = False):
        """Cool down a target solar panel."""
        try:
            if reset:
                self._current_output = 0
            required_power = self._watts_per_degree * self._current_output
            self._power_source.get_power(self._id, required_power)     
            self._time_series.append({
                'index': len(self._time_series),
                'output': self._current_output,
                'target': panel_id
            })
            return self._current_output
        except InsufficientPowerError:
            self._time_series.append({
                'index': len(self._time_series),
                'output': 0,
                'target': panel_id
            })
            return 0                                        # no air-conditioning for you
             