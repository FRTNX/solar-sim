from typing import List, Literal
from simulator_types import Percentage, KiloWatt, Volt
from utils import calculate_watts


class Battery:
    """A battery class."""
    
    def __init__(self, volts: int = 12, amps: int = 50):
        self._id = ''           # todo: generate unique id
        self._volts: Volt = volts
        self._state_of_charge: Percentage = 0.50
        self._max_charge_rate: KiloWatt = 1000
        self._max_discharge_rate: KiloWatt = 1000
        self._depth_of_charge: Percentage = 0.50
        self._amperes: int = amps
        self._available_power: KiloWatt = calculate_watts(self._volts * self._state_of_charge, self._amperes)
        self._capacity: KiloWatt = calculate_watts(self._volts, self._amperes)

    def charge(self, power: KiloWatt):
        """Add to available volts."""
        if power > self._max_charge_rate:
            power = self._max_charge_rate     # limit power to max rate
        if self._available_power + power <= self._capacity:
            self._available_power += power
        self._state_of_charge = self._available_power / self._capacity   
        
    def discharge(self, power: KiloWatt):
        """"""
        
    def status(self):
        return {
            'battery_id': self._id,
            'type': self._volts,
            'capacity': self._capacity,
            'state_of_charge': self._state_of_charge,
            'available_power': { 'unit': 'kilowatt', 'value': self._available_power },
            'voltage': self._available_power / self._amperes
        }
    
    # self.status() is used for internal use where as json is for ui
    def json(self):
        """Return json representation of battery."""
        return self.status()
    

class BatteryArray:
    """Creates a single interface for multiple connected batteries."""
    
    def __init__(self, connection_type: Literal['series', 'parallel'] = 'series'):
        """Create an empty battery array."""
        self._battery_array: List[Battery] = []
        self._capacity: Volt = 0
        self._voltage: Volt = 0
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
            if battery['_id'] == battery_id:
                self._battery_array.pop(self._battery_array.index(battery))
                return { 'result': 'SUCCESS' }
        raise ValueError('BATTERY_NOT_FOUND')
        
    def connected_batteries(self):
        """Return all connected batteries."""
        return self._battery_array
        
    def charge(self, power: KiloWatt):
        """Charge connected batteries, return state"""
        self._distribute_charge(power)
    
    def _distribute_charge(self, power: KiloWatt):
        """Distribute charge equally amongst connected batteries."""
        power_per_battery = power / len(self._battery_array)
        [battery.charge(power_per_battery) for battery in self._battery_array]
        
    def json(self):
        battery_details = [battery.status() for battery in self._battery_array]
        avg_voltage = sum([battery['available_power']['value'] for battery in battery_details]) / len(battery_details)
        return {
            'voltage': avg_voltage,
            'battery_details': battery_details
        }
