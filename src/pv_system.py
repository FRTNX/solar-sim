from typing import List
from simulator_types import Watt, Volt
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
        self._id: str = uuid('PV_SYSTEM')
        self._environment: Environment = environment
        self._panels: SolarArray = panels
        self._batteries: BatteryArray = batteries
        self._inverter: Inverter = Inverter()
        self._total_available_volts: Volt = 0
        self._total_solar_output: Watt = 0
        self._panel_cooling: bool = True
        self._active: bool = False
        self._update_interval: int = 1
        self._iterations_per_day: int = 54
        self._max_iterations: int = 170
        self._iterations: int = 0
        self._time_series: List[dict] = []
        self._metadata: dict = None
        
    def start(self):
        """Activate PV system."""
        if len(self._panels) == 0:
            raise PhotoVoltaicError('Please connect at least one solar panel.')
        if len(self._batteries) == 0:
            raise PhotoVoltaicError('Please connect at least one battery.')
        self._inverter.connect_battery_array(self._batteries)              # connect inverter to battery array
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
        self._max_iterations = value * self._iterations_per_day

    def connect_panel_cooling(self, panel_id):
        """Called after a new solar panel is added to the system's solar array."""
        [
            panel._cooling_system.add_power_source(self._inverter) for panel in self._panels 
            if panel._id == panel_id
        ]
        if not self._panel_cooling:                      # ensure newly added panels conform to existing settings
            self.deactivate_panel_cooling()
        
    def activate_panel_cooling(self):
        """Turn on panel cooling for all solar panels in system."""
        [
            panel._cooling_system.start() for panel in self._panels 
        ]
        self._panel_cooling = True
        
    def deactivate_panel_cooling(self):
        """Turn off panel cooling for all solar panels in system."""
        [
            panel._cooling_system.stop() for panel in self._panels 
        ]
        self._panel_cooling = False

    def update_metadata(self, metadata):
        """Update PV system metadata. Typically the most recently acknowledged client data"""
        self._metadata = metadata

    def _update(self):
        """Get current readings from solar and battery arrays."""
        while self._active:
            panel_details = self._panels.json()
            self._total_solar_output = panel_details['total_output']
            self._batteries.charge(panel_details['total_output']) # send output from solar array to battery array
            battery_details = self._batteries.json()
            self._total_available_volts = battery_details['available_power']
            state = {
                'index': len(self._time_series),                  # 0 based 
                'time': self._environment._integer_time(self._environment._datetime, True),
                'solar_array_output': panel_details['total_output'],
                'battery_array_power': battery_details['available_power']
            }
            self._time_series.append(state)
            if self._iterations > self._max_iterations:
                print('Reached max iterations. Terminating simulation.')
                self.stop()                                       # stop pv system
            else:
                self._iterations += 1
                time.sleep(self._update_interval)
                
    def system_data(self):
        """Return system data."""
        return self._time_series[self._metadata['system']:]  if self._metadata else self._time_series
                
    def panel_data(self):
        """Return current data from all connected panels."""
        return [
            {
                'panel_id': panel._id,
                'rating': panel._power_rating,
                'output': panel._current_output,
                'temperature': panel._current_temperature,
                'efficiency': panel._calculate_efficiency(),
                'time_series': panel._time_series[self._metadata['panels'][panel._id]:] if \
                    self._metadata else panel._time_series
            }
            for panel in self._panels
        ]
    
    def inverter_data(self):
        """Return current inverter data."""
        return {
            'max_output': self._inverter._max_output,
            'output': self._inverter._output_power,
            'time_series': self._inverter._time_series[self._metadata['inverter']:] if self._metadata else \
                self._inverter._time_series
        }
        
    def battery_data(self):
        """Return current battery data."""
        return [
            {
                'battery_id': battery._id,
                'capacity': battery._volts,
                'amps': battery._amperes,
                'soc': battery._state_of_charge,
                'time_series': battery._time_series[self._metadata['batteries'][battery._id]:] \
                    if self._metadata else battery._time_series
            }
            for battery in self._batteries
        ]
    
    def cooling_data(self):
        """Return current cooling systems data."""
        return {
            'cooling': self._panel_cooling,
            'data': [
                {
                    'panel_id': panel._id,
                    'max_output': panel._cooling_system._max_output,
                    'output': panel._cooling_system._current_output,
                    'time_series': panel._cooling_system._time_series[self._metadata['cooling_systems'][panel._id]:] \
                        if self._metadata else panel._cooling_system._time_series
                }
                for panel in self._panels
            ]
        }
        
    def get_iterations(self):
        """Return details about the current simulations iterations."""
        return { 'min': self._iterations, 'max': self._max_iterations }

    def json(self):
        """Return current photovoltaic data.
        """        
        return {
            'system_id': self._id,
            'active': self._active,
            'datetime': self._environment.current_time,
            'current_iteration': self._iterations,
            'max_iteration': self._max_iterations,
            'temperature': self._environment.temperature,
            'solar_irradiance': self._environment.solar_irradiance(),
            'total_solar_output': self._total_solar_output,
            'max_solar_output': sum([panel._power_rating for panel in self._panels]) + (60 * len(self._panels)),
            'aggregated_solar_output': sum([cycle['solar_array_output'] for cycle in self._time_series]),
            'panel_cooling': self._panel_cooling,
            'battery_array_power': self._total_available_volts,
            'battery_array_soc' : self._batteries._avg_state_of_charge,
        }
