from typing import List
from simulator_types import Celcius, Percentage, Watt, KiloWatt, Volt

from environment import Environment
from pv_system import PhotoVoltaicSystem
from solar_panel import SolarPanel, SolarArray
from battery import Battery, BatteryArray

from datetime import datetime
from freezegun import freeze_time

import time
import threading
import fastapi

app = fastapi.FastAPI()


ACTIVE_SIMS: List[PhotoVoltaicSystem] = []


@freeze_time('May 21, 2024', auto_tick_seconds=1800)   # 1 second real time = 30 min sim time
def simulated_time(environment: Environment):
    """Updates an environment's time value based on specified interval."""
    while True:
        environment.set_time(datetime.now())
        time.sleep(1)


def get_pv_system(system_id: str):
    """Get PhotoVoltaicSystem by _id."""
    for system in ACTIVE_SIMS:
        if system._id == system_id:
            return system
    raise ValueError('PVS_NOT_FOUND')


@app.get('/pv/init')
def create_env():
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
    ACTIVE_SIMS.append(system)
    return { 'system': system.state() }


@app.get('/pv/start')
def start_pv_system():
    """Start target PV system."""
    try:
        system_id = ''
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        sim_time_thread = threading.Thread(target=simulated_time, args=(system._environment,))
        sim_time_thread.start()
        system.start()
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }

    
@app.get('/pv/stop')
def stop_pv_system():
    """Stop target PV system."""
    try:
        system_id = ''
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        system.stop()
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }


@app.get('/pv/panel')
def get_panels():
    """Get panels connected to a specified pv system."""
    try:
        system_id = ''
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        return { 'result': [panel.json() for panel in system._panels] }
    except Exception as e:
        return { 'error': str(e) }


@app.post('/pv/panel/add')
def add_panel():
    """Add panel to solar array."""
    try:
        system_id = ''
        pv_system: PhotoVoltaicSystem = get_pv_system(system_id)
        panel = SolarArray({
            'environment': pv_system._environment,
            'standard_conditions': {
                'power_rating': 100,
                'efficiency': 0.23,
                'temparature': { 'unit': 'Celcius', 'value': 25 }
            },
            'temp_coefficient': 0.11,
            'area': 3
        })
        pv_system._panels.add(panel)
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }


@app.post('/pv/panel/remove')
def remove_panel():
    """"""
    
# @app.get('/pv/battery')

# @app.post('/pv/battery/add')

# @app.delete('/pv/battery/remove')
