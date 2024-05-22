from typing import List, Tuple, Union
from simulator_types import Celcius, Percentage, Watt, KiloWatt, Volt

from datetime import datetime
from freezegun import freeze_time

import time
import json
import threading

from fastapi import FastAPI


class Environment:
    """Simulates environemt, overseeing the passage of time."""
    
    def __init__(self):
        """Initialise environment in 'frozen' state."""
        self._datetime = ''
        self._active = False
        self._update_interval = 1
        self._max_solar_irradiance: Watt = 1000
        self._zenith_time = 1200
        self._temparature: Celcius  = 25
        # todo: factor in real time weather data based on location
        
    @property
    def current_time(self):
        """Time adapter function."""
        return str(self._datetime)
    
    @property
    def zenith_time(self):
        return self._zenith_time
    
    @property
    def max_solar_irradiance(self):
        return self._max_solar_irradiance
    
    @property
    def temparature(self):
        # todo: calculate by distance from zenith/noon
        return self._temparature
    
    def solar_irradiance(self):
        """Calculate current solar irradiance with respect to time."""
        loss = abs(self.zenith_time - self._integer_time(self._datetime))
        irradiance = self.max_solar_irradiance - loss
        return irradiance if irradiance > 0 else 0
        
    def set_time(self, simulated_time: datetime):
        self._datetime = simulated_time
            
    def _integer_time(self, date_time: datetime):
        """Return time as an integer for mock solar irradiance calculations."""
        try:
            int_time = int(date_time.strftime('%X').replace(':', '')[:4])
            return int_time
        except:
            return 0
        

def calculate_volts(watts, amps):
    """Calculate voltage from watts and amperes."""
    return watts / amps


def calculate_watts(volts, amps):
    """Calculate watts from voltage and amperes."""
    return volts * amps

        
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
    

class BatteryArray:
    """Creates a single interface for multiple connected batteries."""
    
    def __init__(self):
        """Create an empty battery array."""
        self._battery_array = []
        self._capacity: Volt = 0
        self._voltage: Volt = 0
        self._connection_type = None
        self._time_series = []
        
    def add(self, battery: Battery, connection_type: str='series'):
        """Connect a new battery."""
        # todo: validate battery compatability
        self._battery_array.append(battery)
        return { 'result': 'SUCCESS' }
        
    def remove(self, battery_id):
        for battery in self._battery_array:
            if battery['_id'] == battery_id:
                self._battery_array.pop(self._battery_array.index(battery))
                return { 'result': 'SUCCESS' }
        return { 'error': 'BATTERY_NOT_FOUND' }
        
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
        
    def get_battery_details(self):
        battery_details = [battery.status() for battery in self._battery_array]
        avg_voltage = sum([battery['available_power']['value'] for battery in battery_details]) / len(battery_details)
        return {
            'voltage': avg_voltage,
            'battery_details': battery_details
        }


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
        
    def _get_power_output(self):
        """Takes solar irradiance and panel temparature as input, returns panel power
        output in watts."""
        solar_irradiance = self._environment.solar_irradiance() * self._area
        efficiency = self._calculate_efficiency()
        return (solar_irradiance * efficiency) / 3
        
    def _calculate_efficiency(self):
        """"""
        if self._current_temparature > self._optimal_temparature:
            degrees_above_threshold = self._current_temparature - self._optimal_temparature
            temparature_correction_factor = self._temparature_coefficient * degrees_above_threshold
            return self._efficiency - temparature_correction_factor
        else:
            return self._efficiency
        
    def _get_panel_temparature(self):
        """Calculate panel temparature based on environment temparatures and cooling factors."""
        environment_temp = self._environment.temparature
        return environment_temp - self._cooling_factors()
        
    def _cooling_factors(self):
        """Returns the temparature drop accounted for by water and air conditioners."""
        return 0      # todo: add appropriate mechanisms


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
        self._array_temparature = sum(panel_temps) / len(panel_temps)
        self._total_output = sum([panel['power_output'] for panel in panel_details])
        return {
            'array_temparature': self._array_temparature,
            'total_output': self._total_output,
            'panel_details': panel_details
        }

    
class PhotoVoltaicSystem:
    """Simulates a PV system; records state changes over time."""
    
    def __init__(self, environment: Environment, panels: SolarArray, batteries: BatteryArray):
        self._environment: Environment = environment
        self._panels: SolarArray = panels
        self._batteries: BatteryArray = batteries
        self._total_available_volts: Volt = 0
        self._totol_solar_output: Watt = 0
        self._active: bool = False
        self._update_interval: int = 1
        self._time_series: List[dict] = []
        
    def start(self):
        """Activate PV system."""
        self._active = True
        update_thread = threading.Thread(target=self._update)
        update_thread.start()
        
    def stop(self):
        """Deactivate PV system."""
        self._active = False

    def state(self):
        """Return most recent state."""
        if len(self._time_series) > 0:
            return self._time_series[-1]
        return None
    
    def _update(self):
        """Get current readings from solar and battery arrays."""
        while self._active:
            self._charge_battery_array()        # send output from solar array to battery array
            panel_details = self._panels.get_panel_details()
            battery_details = self._batteries.get_battery_details()
            state = {
                'time': self._environment.current_time,
                'panel_details': panel_details,
                'battery_details': battery_details
            }
            self._time_series.append(state)
            time.sleep(self._update_interval)
            
    def _charge_battery_array(self):
        panel_details = self._panels.get_panel_details()
        self._batteries.charge(panel_details['total_output'])


@freeze_time('May 21, 2024', auto_tick_seconds=1800)   # 1 second real time = 30 min sim time
def simulated_time(environment: Environment):
    """Updates an environment's time value based on specified interval."""
    while True:
        environment.set_time(datetime.now())
        time.sleep(1)


if __name__ == '__main__':
    environment = Environment()
    panel = SolarPanel({
        'environment': environment,
        'standard_conditions': {
            'power_rating': 100,
            'efficiency': 0.23,    # where 1.0 = 100% and 0.01 = 1%
            'temparature': { 'unit': 'Celcius', 'value': 25 }
        },
        'temp_coefficient': 0.11,
        'area': 3                  # meters squared
    })
    battery = Battery(volts=12, amps=100)
    solar_array = SolarArray()
    battery_array = BatteryArray()
    solar_array.add(panel)
    battery_array.add(battery)
    system = PhotoVoltaicSystem(environment=environment, panels=solar_array, batteries=battery_array)
    sim_time_thread = threading.Thread(target=simulated_time, args=(environment,))
    sim_time_thread.start()
    system.start()
    while True:
        print(json.dumps(system.state()))
        time.sleep(2)
