from typing import List, Tuple, Union
from simulator_types import Celcius, Percentage, Watt, KiloWatt, Volt

import time
import threading


class Environment:
    """Simulates environemt, overseeing the passage of time."""
    
    def __init__(self):
        """Initialise environment in 'frozen' state."""
        self._time = Time()
        self._active = False
        self._update_interval = 1
        self._max_solar_irradiance: Watt = 1000
        self._zenith_time = 1200
        self._temparature: Celcius  = 25
        # todo: factor in real time weather data based on location
        
    @property
    def current_time(self):
        """Time adapter function."""
        return self._time.get_time()
    
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
        loss = abs(self.zenith_time - self.current_time)
        irradiance = self.max_solar_irradiance - loss
        return irradiance if irradiance > 0 else 0
        
    def start(self):
        """Start space-time.""" 
        self._active = True
        update_thread = threading.Thread(target=self._update)
        update_thread.start()
        
    def stop(self):
        """Stop space-time."""
        self._active = False
        
    def _update(self):
        while self._active:
            self._cycle()
            time.sleep(self._update_interval)
    
    def _cycle(self):
        """Change state by one cycle."""
        self._time.tick()

# todo: improve to work well in time-series analysis
class Time:
    """Simulate time."""
    
    def __init__(self, initial_time: int=0):
        self._time = initial_time
        
    def get_time(self):
        """Return current time."""
        return self._time
    
    def tick(self, value: int=1):
        """Increment time by value."""
        if self._time < 2359:                       # 24-hour format
            self._time += value
        else:
            self._time = 0                          # reset

        
class Battery:
    """A battery class."""
    
    def __init__(self, voltage: int = 12, amps: int = 50):
        self._id = ''           # todo: generate unique id
        self._voltage = 12
        self._amperes = amps
        self._available_volts = 12.2
        self._solar_panel: SolarArray = None  
        self._charge_controller = None
        self._time_series = []

    def charge(self, watts: int):
        """Add to available volts."""
        if self._solar_panel:
            watts = self._solar_panel.discharge()
        
    def discharge(self, volts):
        """"""
        
    def status(self):
        return {
            'battery_id': self._id,
            'volts': self._available_volts
        }
    

class BatteryArray:
    """Creates a single interface for multiple connected batteries."""
    
    def __init__(self):
        """"""
        self._batteries = []
        self._capacity: Volt = 0
        self._voltage: Volt = 0
        self._connection_type = None
        self._time_series = []
        
    def add(self, battery: Battery, connection_type: str='series'):
        """Connect a new battery."""
        # todo: validate compatability
        self._batteries.append(battery)
        return { 'result': 'SUCCESS' }
        
    def remove(self, battery_id):
        for battery in self._batteries:
            if battery['_id'] == battery_id:
                self._batteries.pop(self._batteries.index(battery))
                return { 'result': 'SUCCESS' }
        return { 'error': 'BATTERY_NOT_FOUND' }
        
    def connected_batteries(self):
        """Return all connected batteries."""
        return self._batteries
        
    def charge(self, charge_details: dict):
        """"""
        self._distribute_charge(charge_details)    
    
    def _distribute_charge(self, charge):
        """Distribute charge equally amongst connected batteries."""
        
    def get_battery_details(self):
        battery_details = [battery.status() for battery in self._batteries]
        avg_voltage = sum([battery['volts'] for battery in battery_details]) / len(battery_details)
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
        # self._update()
        solar_irradiance = self._solar_irradiance() * self._area
        efficiency = self._calculate_efficiency()
        return solar_irradiance * efficiency
        
    def _solar_irradiance(self):
        """Returns solar irradiance with respect to time.""" # todo: factor location and weather
        return self._environment.solar_irradiance()
        
    def _calculate_efficiency(self):
        """"""
        if self._current_temparature > self._optimal_temparature:
            degrees_above_threshold = self._current_temparature - self._optimal_temparature
            temparature_correction_factor = self._temparature_coefficient * degrees_above_threshold
            return self._efficiency - temparature_correction_factor
        else:
            return self._efficiency
        
    def _cooling_factors(self):
        """Returns the temparature drop accounted for by water and air conditioners."""
        return 0      # todo: add appropriate mechanisms
        
    def _get_panel_temparature(self):
        """Calculate panel temparature based on environment temparatures and cooling factors."""
        environment_temp = self._environment.temparature
        return environment_temp - self._cooling_factors()


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
            panel_details = self._panels.get_panel_details()
            battery_details = self._batteries.get_battery_details()
            state = {
                'time': self._environment.current_time,
                'panel_details': panel_details,
                'battery_details': battery_details
            }
            self._time_series.append(state)
            time.sleep(self._update_interval)


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
    battery = Battery(voltage=12, amps=50)
    solar_array = SolarArray()
    battery_array = BatteryArray()
    solar_array.add(panel)
    battery_array.add(battery)
    system = PhotoVoltaicSystem(environment=environment, panels=solar_array, batteries=battery_array)
    environment.start()
    system.start()
    while True:
        print(system.state())
        time.sleep(2)
