from typing import List, Tuple, Union

import time
import threading


class SpaceTime:
    """Simulates spacetime, overseeing the passage of time."""
    
    def __init__(self):
        """Initialise spacetime in 'frozen' state."""
        self._time = Time()
        self._active = False
        self._update_interval = 1
        # todo: factor in real time weather data based on location
        
    @property
    def current_time(self):
        """Time adapter function."""
        return self._time.get_time()
        
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


class Sun:
    """Simulates the sun at various times of the day."""
    
    def __init__(self, spacetime: SpaceTime):
        self._spacetime = spacetime
        self._max_photons = 600
        self._zenith_time = 1200
        # todo: populate state from NASA coronal data
    
    # todo: improve time calculations: switch to base 60
    def discharge_photons(self):
        """Descharge photons with respect to time of day."""
        loss = abs(self._zenith_time - self._spacetime.current_time)
        photons = self._max_photons - loss
        return photons if photons >= 0  else 0

        
class Battery:
    """A battery class."""
    
    def __init__(self, voltage: int = 12, amps: int = 50):
        self._identifier = ''           # todo: generate unique id
        self._voltage = 12
        self._amperes = amps
        self._available_volts = 12.2
        self._solar_panel: SolarInput = None  
        self._charge_controller = None
        self._time_series = []
        
    def charge(self, watts: int):
        """Add to available volts."""
        if self._solar_panel:
            watts = self._solar_panel.discharge()
        
    def discharge(self, volts):
        """"""
    
    @property
    def available_volts(self):
        return self._available_volts
    

class BatteryArray:
    """Creates a single interface for multiple connected batteries."""
    
    def __init___(self):
        """"""
        self._batteries: List[Battery] = []
        self._capacity = 0
        self._voltage = 0
        self._connection_type = None
        self._time_series = []
        
    def connect_battery(self, battery: Battery, connection_type: str='series'):
        """Connect a new battery."""
        
    def connected_batteries(self):
        """Return all connected batteries."""
        return self._batteries
        
    def charge(self, charge_details: dict):
        """"""
        self._distribute_charge(charge_details)    
    
    def _distribute_charge(self, charge):
        """Distribute charge equally amongst connected batteries."""


class SolarPanel:
    """A solar panel."""
    
    def __init__(self, spacetime: SpaceTime, sun: Sun, watts: int = 100):
        self._watts = watts
        self._temparature = 0
        self._temparature_coefficient = 0
        self._photons = 0
        self._sun = sun
        self._time_series = []
        
    def discharge(self):
        """"""
        return self._photons_to_watts(self._sun.discharge_photons())
        
    @property
    def captured_photons(self):
        return self._photons
    
    # todo: account for standard testing conditions (STC)
    def _photons_to_watts(self, photons):
        """Converts photons to watts."""
        # todo: use watts = volts x amps
        return photons // 4


class SolarArray:
    """Creates a single interface to an array of solar panels."""
    
    def __init__(self):
        """Create an empty solar panel array."""
        self._panels = []
        
    def add_panel(self, panel: SolarPanel):
        """Add a solar panel to the array."""
        self._panels.append(panel)

    
class PhotoVoltaicSystem:
    """Simulates a PV system; captures state change over time."""
    
    def __init__(self, spacetime: SpaceTime, panels: List[SolarPanel], batteries: List[Battery]):
        self._spacetime = spacetime
        self._panels = panels
        self._batteries = batteries
        self._total_available_volts = 0
        self._total_captured_photons = 0
        self._time_series = []
        
    def state(self):
        state = {
            'time': self._spacetime.current_time,
            'battary_voltage': self._total_available_volts,
            'captured_photons': self._total_captured_photons
        }
        self._time_series.append(state)
        return state
    
    
SolarInput = Union[SolarPanel, SolarArray]
    
if __name__ == '__main__':
    spacetime = SpaceTime()
    sun = Sun(spacetime=spacetime)
    panel = SolarPanel(spacetime=spacetime, sun=sun) # todo: factor panel angle/orientation
    battery = Battery(voltage=12, amps=50)
    system = PhotoVoltaicSystem(spacetime=spacetime, panels=[panel], batteries=[battery])
    spacetime.start()
    while True:
        print(system.state())
        time.sleep(2)
