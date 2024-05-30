from simulator_types import Watt, Volt, Ampere
from typing import List

from battery import BatteryArray
from utils import InsufficientPowerError

class LoadError(Exception):
    """"""
    pass

class Inverter:
    """Converts DC power from the battery array to AC power."""
    
    def __init__(self):
        """Initialise a new inverter."""
        self._max_output: Watt = 1500
        self._input_voltage: Volt = 0
        self._input_current: Ampere = 0
        self._output_voltage: Volt = 0
        self._output_current: Ampere = 0
        self._output_power: Watt = 0
        self._battery_array: BatteryArray = None
        self._load_error: bool = False
        self._active: bool = False
        self._appliances: dict = {}
        self._time_series: List[dict] = []
        
    def start(self):
        """Start inverter."""
        self._active = True
        
    def stop(self):
        """Switch off inverter."""
        self._active = False
    
    def reset(self):
        """Reset inverter after load error."""
        self._load_error = False

    def connect_battery_array(self, battery_array: BatteryArray):
        """Connect inverter to battery array."""
        self._battery_array = battery_array
    
    # when an appliance requests power for the first time, it is added to self._appliances
    # along with its requested power. the power output value will change with each iteration
    # ideally, all appliances should eventually request 0 watts of power.
    def get_power(self, appliance_id: str, power: Watt):
        """Get requested power, if available."""
        self._output_power = self._get_total_output()
        requested_power = self._output_power + power
        if requested_power > self._max_output:
            raise LoadError('Requested power exceeds inverter specifications.')
        
        if self._battery_array._total_available_power > requested_power:
            self._appliances[appliance_id] = { 'output': power }      # add or update appliance power requirements
            self._output_power = requested_power
            state = { 'output': self._output_power }
            self._time_series.append(state)
            return self._battery_array.discharge(power)
        
        # requested power is more than available power
        state = { 'output': 0 }
        self._time_series.append(state)
        self._load_error = True
        raise InsufficientPowerError('Not enough power in batteries.')
    
    def _get_total_output(self):
        """Get current total power output across all appliances."""
        return sum([
            self._appliances[appliance]['output'] for appliance in self._appliances
            if len(self._appliances) > 0
        ])
        
    def _convert_to_ac(self):
        """"""
