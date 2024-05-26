from simulator_types import Celcius, Watt
from utils import uuid

from datetime import datetime


class Environment:
    """Simulates environemt, overseeing the passage of time."""
    
    def __init__(self):
        """Initialise environment in 'frozen' state."""
        self._id = uuid('ENVIRON')
        self._datetime = ''
        self._active = True
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
    
    def start(self):
        """Start environment."""
        self._active = True
        
    def stop(self):
        """Stop environment."""
        self._active = False
    
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
        
    def json(self):
        """Return json representation of environment."""
