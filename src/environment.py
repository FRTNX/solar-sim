from simulator_types import Celcius, Watt
from typing import List, Union
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
        self._min_solar_irradiance: Watt = 0
        self._max_solar_irradiance: Watt = 2000
        self._temperature: Celcius = 0
        self._minumum_temperature: Celcius = 4
        self._maximum_temperature: Celcius = 35
        # todo: factor in real time weather data based on location
        
    @property
    def current_time(self):
        """Time adapter function."""
        return str(self._datetime)

    @property
    def max_solar_irradiance(self):
        return self._max_solar_irradiance
    
    @property
    def temperature(self):
        return self._temperature
        
    def stop(self) -> None:
        """Stop environment."""
        self._active = False
    
    def solar_irradiance(self) -> Union[int, float]:
        """Calculate current solar irradiance with respect to time."""
        hour, minute = self._split_time(self._datetime)
        if hour < 6 or hour >= 18:                                # handle night time irradiance
            return self._min_solar_irradiance        
        if hour >= 12:                                            # invert all time values after 12
            time = self._invert_time(hour, minute)
        else:
            time = hour + (minute / 60)
        return self._min_solar_irradiance + ((self._max_solar_irradiance - self._min_solar_irradiance) / 12) * (time - 6)
        
    def set_time(self, simulated_time: datetime):
        self._datetime = simulated_time
        self._update_temperature()                                 # changes in time typically include temperature changes
        
    def _update_temperature(self) -> None:
        """Update environment temperature based on time of day (typically by hour)."""
        hour, minute = self._split_time(self._datetime)
        time = hour
        if hour >= 12:
            time = self._invert_time(hour, minute)
        else:
            time = hour + (minute / 60)
        fraction_of_day = time / 12
        self._temperature = self._minumum_temperature + ((self._maximum_temperature - \
            self._minumum_temperature) * fraction_of_day) 
        
    def _invert_time(self, hour: int, minute: int) -> List[int]:
        """Invert time values. Creates time parabola."""
        diff = hour - 12
        return (hour - (diff * 2)) - (minute / 60)
        
    def _split_time(self, date_time: datetime):                     # todo: move to utils
        """Helper function."""
        try:
            hour, minute = date_time.strftime('%X')[:5].split(':')
            return [int(hour), int(minute)]
        except:
            return [0, 0]
            
    def _integer_time(self, date_time: datetime, select_hour: bool = False) -> int:
        """Return time as an integer for mock solar irradiance calculations."""
        try:
            limit = 2 if select_hour else 4
            int_time = int(date_time.strftime('%X').replace(':', '')[:limit])
            return int_time
        except:
            return 0
        
    def json(self):
        """Return json representation of environment."""
