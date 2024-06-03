from typing import List, Literal
from simulator_types import Percentage, Watt, Volt
from utils import calculate_watts, uuid


class LoadError(Exception):
    """"""
    pass

class Battery:
    """A battery class."""
    
    def __init__(self, volts: int = 12, amps: int = 50):
        self._id = uuid('BATTERY')
        self._volts: Volt = volts
        self._state_of_charge: Percentage = 0.01
        self._minimum_power: Watt = 0
        self._max_charge_rate: Watt = 1000
        self._max_discharge_rate: Watt = 1000
        self._depth_of_charge: Percentage = 0.50
        self._amperes: int = amps
        self._available_power: Watt = calculate_watts(self._volts * self._state_of_charge, self._amperes)
        self._capacity: Watt = calculate_watts(self._volts, self._amperes)
        self._time_series = []

    def status(self):
        state = {
            'battery_id': self._id,
            'capacity': self._capacity,
            'state_of_charge': self._state_of_charge,
            'available_power': self._available_power,
            'voltage': self._available_power / self._amperes
        }
        self._time_series.append(state)
        return state
    
    def charge(self, power: Watt):
        """Add power to battery."""
        if power > self._max_charge_rate:
            power = self._max_charge_rate     # limit power to max rate
        if self._available_power + power <= self._capacity:
            self._available_power += power
        self._state_of_charge = self._available_power / self._capacity   
        
    def discharge(self, power: Watt):
        """Discharge power from battery."""
        if power > self._max_discharge_rate:
            raise LoadError('Requested power exceeds maximum discharge rate.')
        if self._available_power - power > self._minimum_power:
            self._available_power -= power
        self._state_of_charge = self._available_power / self._capacity
            
    def json(self):     # self.status() is used for internal use where as json is for ui
        """Return json representation of battery."""
        return {
            'battery_id': self._id,
            'type': self._volts,
            'capacity': self._capacity,
            'state_of_charge': self._state_of_charge,
            'available_power': { 'unit': 'watt', 'value': self._available_power },
            'voltage': self._available_power / self._amperes
        }
    

class BatteryArray:
    """Creates a single interface for multiple connected batteries."""
    
    def __init__(self, connection_type: Literal['series', 'parallel'] = 'series'):
        """Create an empty battery array."""
        self._id = uuid('B_ARRAY')
        self._battery_array: List[Battery] = []
        self._capacity: Volt = 0
        self._voltage: Volt = 0
        self._avg_state_of_charge = 0.0
        self._total_available_power: Watt = 0
        self._connection_type: str = connection_type
        self._time_series = []
        
    def __iter__(self):
        for battery in self._battery_array:
            yield battery
            
    def __len__(self):
        return len(self._battery_array)
        
    def add(self, battery: Battery):
        """Connect a new battery."""
        # todo: validate battery compatability
        self._battery_array.append(battery)
        return { 'result': 'SUCCESS' }

    def get(self, battery_id: str):
        """Get target battery details."""
        for battery in self._battery_array:
            if battery._id == battery_id:
                return battery.json()
        raise ValueError('BATTERY_NOT_FOUND')
        
    def remove(self, battery_id):
        for battery in self._battery_array:
            if battery._id == battery_id:
                self._battery_array.pop(self._battery_array.index(battery))
                return { 'result': 'SUCCESS' }
        raise ValueError('BATTERY_NOT_FOUND')
        
    def connected_batteries(self):
        """Return all connected batteries."""
        return self._battery_array
        
    def charge(self, power: Watt):
        """Charge connected batteries, return state"""
        self._distribute_charge(power)
        
    def discharge(self, power: Watt):
        """Discharge power from connected batteries."""
        try:
            self._distribute_discharge(power)
            return power
        except LoadError:
            return 0
    
    def _distribute_charge(self, power: Watt):
        """Distribute charge equally amongst connected batteries."""
        power_per_battery = power / len(self._battery_array)
        [battery.charge(power_per_battery) for battery in self._battery_array]
    
    def _distribute_discharge(self, power: Watt):
        """Distribute discharge equally amongst connected batteries."""
        power_per_battery = power / len(self._battery_array)
        [battery.discharge(power_per_battery) for battery in self._battery_array]

    def json(self):
        """Return json representation of battery array."""
        battery_details = [battery.status() for battery in self._battery_array]
        avg_voltage = sum([battery['available_power'] for battery in battery_details]) / len(battery_details)
        avg_state_of_charge = sum([battery['state_of_charge'] for battery in battery_details]) / len(battery_details)
        total_power = sum([battery['available_power'] for battery in battery_details])
        self._total_available_power = total_power
        self._avg_state_of_charge = avg_state_of_charge
        self._voltage = avg_voltage
        return {
            'array_id': self._id,
            'available_power': avg_voltage,
            'batteries': battery_details,
            'avg_state_of_charge': avg_state_of_charge
        }
