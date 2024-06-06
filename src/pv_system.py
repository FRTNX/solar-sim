from typing import List
from simulator_types import Watt, Volt, Celcius, Ampere
from utils import uuid, PhotoVoltaicError

from environment import Environment
from inverter import Inverter

from solar_panel import SolarArray
from battery import BatteryArray

import time
import threading

        
class PhotoVoltaicSystem:
    """Simulates a PV system; records state changes over time."""
    
    def __init__(self, environment: Environment, panels: SolarArray, batteries: BatteryArray):
        self._id = uuid('PV_SYSTEM')
        self._environment: Environment = environment
        self._panels: SolarArray = panels
        self._batteries: BatteryArray = batteries
        self._inverter: Inverter = Inverter()
        self._total_available_volts: Volt = 0
        self._total_solar_output: Watt = 0
        self._panel_cooling: bool = True
        self._active: bool = False
        self._update_interval: int = 1
        self._iterations_per_day = 84
        self._max_iterations = 252                                    # (84 * 3) days
        self._iterations = 0
        self._time_series: List[dict] = []
        
    def start(self):
        """Activate PV system."""
        if len(self._panels) == 0:
            raise PhotoVoltaicError('Please connect at least one solar panel.')
        if len(self._batteries) == 0:
            raise PhotoVoltaicError('Please connect at least one battery.')
        # connect inverter to battery array
        self._inverter.connect_battery_array(self._batteries)
        # connect solar panel cooling systems to inverter
        [panel._cooling_system.add_power_source(self._inverter) for panel in self._panels]
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
    
    def set_max_iteration(self, value: int):
        """Set max iterations. Gives the client control of simulation length.
        
        value: integer value representing the number of days to run the sim.
        """
        # todo: make sure value is greater than current iterations
        self._max_iterations = value * self._iterations_per_day

    def connect_panel_cooling(self, panel_id):
        """Called after a new solar panel is added to the systems solar array."""
        [
            panel._cooling_system.add_power_source(self._inverter) for panel in self._panels 
            if panel._id == panel_id
        ]
        if not self._panel_cooling:                      # ensure newly added panels conform to existing settings
            self.deactivate_panel_cooling()
        
    def activate_panel_cooling(self):
        """Turn on panel cooling for all panels in system."""
        [
            panel._cooling_system.start() for panel in self._panels 
        ]
        self._panel_cooling = True
        
    def deactivate_panel_cooling(self):
        """Turn off panel cooling for all panels in system."""
        [
            panel._cooling_system.stop() for panel in self._panels 
        ]
        self._panel_cooling = False

    def _update(self):
        """Get current readings from solar and battery arrays."""
        while self._active:
            panel_details = self._panels.json()
            battery_details = self._batteries.json()
            self._batteries.charge(panel_details['total_output']) # send output from solar array to battery array
            self._total_solar_output = panel_details['total_output']
            self._total_available_volts = battery_details['available_power']
            state = {
                'time': self._environment._integer_time(self._environment._datetime, True),
                'solar_array_output': panel_details['total_output'],
                'battery_array_power': battery_details['available_power'],
                
            }
            self._time_series.append(state)
            if self._iterations > self._max_iterations:
                print('Reached max iterations. Terminating simulation.')
                self.stop()                                       # stop pv system
                self._environment.stop()                          # stop environment
            else:
                self._iterations += 1
                time.sleep(self._update_interval)

    def json(self, metadata=None):
        """Return json representation of PV system. The metadata argument helps us return only
        data that the client does not already have.
        """
        print('got metadata: ', metadata)
        # if metadata and metadata['system'] == 0:
        #     metadata = None
        metadata = None                                 # disable feature fn
        
        return {
            'system_id': self._id,
            'active': self._active,
            'current_iteration': self._iterations,
            'max_iteration': self._max_iterations,
            'datetime': self._environment.current_time,
            'total_solar_output': self._total_solar_output,
            'battery_array_power': self._total_available_volts,
            'battery_array_soc' : self._batteries._avg_state_of_charge,
            'solar_irradiance': self._environment.solar_irradiance(),
            'temperature': self._environment.temperature,
            'max_solar_output': sum([panel._power_rating for panel in self._panels]) + (60 * len(self._panels)),
            'panel_cooling': self._panel_cooling,
            'aggregated_solar_output': sum([cycle['solar_array_output'] for cycle in self._time_series]),
            'time_series': self._time_series[metadata['system']:]  if metadata else self._time_series,
            'inverter': {
                'max_output': self._inverter._max_output,
                'output': self._inverter._output_power,
                'time_series': self._inverter._time_series[metadata['inverter']:] if metadata else self._inverter._time_series
            },
            'panels': [
                {
                    'panel_id': panel._id,
                    'rating': panel._power_rating,
                    'output': panel._current_output,
                    'temperature': panel._current_temperature,
                    'efficiency': panel._calculate_efficiency(),
                    'time_series': panel._time_series[metadata['panels'][panel._id]:] if metadata else panel._time_series
                }
                for panel in self._panels
            ],
            'batteries': [
                {
                    'battery_id': battery._id,
                    'capacity': battery._volts,
                    'amps': battery._amperes,
                    'soc': battery._state_of_charge,
                    'time_series': battery._time_series[metadata['batteries'][battery._id]:] if metadata else battery._time_series
                }
                for battery in self._batteries
            ],
            'cooling_systems': [
                {
                    'panel_id': panel._id,
                    'max_output': panel._cooling_system._max_output,
                    'output': panel._cooling_system._current_output,
                    'time_series': panel._cooling_system._time_series[metadata['cooling_systems'][panel._id]:] if metadata else panel._cooling_system._time_series
                }
                for panel in self._panels
            ]
        }
