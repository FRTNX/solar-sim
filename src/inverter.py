from simulator_types import Watt, Volt, Ampere
from battery import BatteryArray

from utils import InsufficientPowerError

class Inverter:
    """Converts DC power from the battery array to AC power."""
    
    def __init__(self):
        """Initialise a new inverter."""
        self._max_watts: Watt = 1500
        self._input_voltage: Volt = 0
        self._input_current: Ampere = 0
        self._output_voltage: Volt = 0
        self._output_current: Ampere = 0
        self._output_power: Watt = 0
        self._battery_array: BatteryArray = None
        self._load_error: bool = False
        self._active = False
        self._time_series = []
        
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
        
    def get_power(self, power: Watt):
        """Get requested power, if available."""
        if self._battery_array._total_available_power > power:
            state = { 'output': power }
            self._time_series.append(state)
            return self._battery_array.discharge(power)
        # requested power is more than available power
        state = { 'output': 0 }
        self._time_series.append(state)
        self._load_error = True
        raise InsufficientPowerError('Not enough power!')
        
    def _convert_to_ac(self):
        """"""
