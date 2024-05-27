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
        self._temparature: Celcius = 0
        self._minumum_temparature: Celcius = 9
        self._maximum_temparature: Celcius = 35
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
        self._update_temparature()           # changes in time typically include temparature changes
        
    def _update_temparature(self):
        """Update environment temparature based on time of day (typically by hour)."""
        hour = self._integer_time(self._datetime, True)
        if hour > 12:                        # make all hours after midday the inverse of those before noon
            diff = hour - 12
            hour = hour - (diff * 2)
        fraction_of_day = hour / 12
        temparature = self._minumum_temparature + ((self._maximum_temparature - self._minumum_temparature) * fraction_of_day)
        self._temparature = temparature
            
    def _integer_time(self, date_time: datetime, select_hour: bool = False):
        """Return time as an integer for mock solar irradiance calculations."""
        try:
            limit = 2 if select_hour else 4
            int_time = int(date_time.strftime('%X').replace(':', '')[:limit])
            return int_time
        except:
            return 0
        
    def json(self):
        """Return json representation of environment."""
