from typing import List
from simulator_types import Watt, Volt
from utils import uuid, PhotoVoltaicError

from environment import Environment
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
        self._total_available_volts: Volt = 0
        self._total_solar_output: Watt = 0
        self._active: bool = False
        self._update_interval: int = 1
        self._max_iterations = 100
        self._iterations = 0
        self._time_series: List[dict] = []
        
    def start(self):
        """Activate PV system."""
        if len(self._panels) == 0:
            raise PhotoVoltaicError('Please connect at least one solar panel.')
        if len(self._batteries) == 0:
            raise PhotoVoltaicError('Please connect at least one battery.')
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
            self._charge_battery_array()                            # send output from solar array to battery array
            panel_details = self._panels.json()
            battery_details = self._batteries.json()
            self._total_solar_output = panel_details['total_output']
            self._total_available_volts = battery_details['voltage']
            state = {
                'time': self._environment._integer_time(self._environment._datetime, True),
                'solar_array_output': panel_details['total_output'],
                'battery_array_power': battery_details['voltage'],
                
            }
            self._time_series.append(state)
            if self._iterations > self._max_iterations:
                print('Reached max iterations. Terminating simulation.')
                self.stop()                                       # stop pv system
                self._environment.stop()                          # stop environment
            else:
                self._iterations += 1
                time.sleep(self._update_interval)
            
    def _charge_battery_array(self):
        panel_details = self._panels.json()
        self._batteries.charge(panel_details['total_output'])

    def json(self):
        """Return json representation of PV system."""
        return {
            'system_id': self._id,
            'active': self._active,
            'datetime': self._environment.current_time,
            'total_solar_output': self._total_solar_output,
            'battery_array_power': self._total_available_volts,
            'battery_array_soc' : self._batteries._avg_state_of_charge,
            'solar_irradiance': self._environment.solar_irradiance(),
            'temparature': self._environment.temparature,
            'time_series': self._time_series,
            'panels': [
                {
                    'panel_id': panel._id,
                    'rating': panel._power_rating,
                    'output': panel._current_output,
                    'temparature': panel._current_temparature,
                    'efficiency': panel._calculate_efficiency(),
                    'time_series': panel._time_series
                }
                for panel in self._panels
            ],
            'batteries': [
                {
                    'battery_id': battery._id,
                    'capacity': battery._volts,
                    'amps': battery._amperes,
                    'soc': battery._state_of_charge,
                    'time_series': battery._time_series
                }
                for battery in self._batteries
            ]
        }
