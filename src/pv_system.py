from typing import List
from simulator_types import Watt, Volt

from environment import Environment
from solar_panel import SolarArray
from battery import BatteryArray

import time
import threading


class PhotoVoltaicSystem:
    """Simulates a PV system; records state changes over time."""
    
    def __init__(self, environment: Environment, panels: SolarArray, batteries: BatteryArray):
        self._id = ''
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
            [panel.update_temparature() for panel in self._panels]  # update panel temparature based on env temp
            self._charge_battery_array()                            # send output from solar array to battery array
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
