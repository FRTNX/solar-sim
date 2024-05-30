from typing import List, Union
from typing_extensions import TypedDict

from environment import Environment
from pv_system import PhotoVoltaicSystem
from solar_panel import SolarPanel, SolarArray
from battery import Battery, BatteryArray

from datetime import datetime
from freezegun import freeze_time

import time
import threading
import fastapi

from starlette.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


ACTIVE_SIMS: List[PhotoVoltaicSystem] = []


class temperatureDict(TypedDict):
    unit: str
    value: Union[int, float]

class IncomingSTC(TypedDict):
    power_rating: int
    efficiency: float
    temperature: temperatureDict

class IncomingBattery(TypedDict):
    system_id: str
    volts: Union[int, float]
    amps: int
    
class IncomingSolarPanel(TypedDict):
    system_id: str
    stc: IncomingSTC
    temp_coefficient: Union[int, float]
    area: Union[int, float]

@freeze_time('May 21, 2024 04:00', auto_tick_seconds=300)   # 1 second real time = 30 min sim time
def simulated_time(environment: Environment):
    """Updates an environment's time value based on specified interval."""
    while environment._active:
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
    environment = Environment()                    # initialise environment
    solar_array = SolarArray()                     # create empty solar array
    battery_array = BatteryArray()                 # create empty battery array
    system = PhotoVoltaicSystem(environment=environment, panels=solar_array, batteries=battery_array)
    ACTIVE_SIMS.append(system)
    return { 'result': system.json() }

@app.get('/pv/init/default')
def create_default_sim():
    """Initialise and start default simulation: environment, a panel and a battery."""
    environment = Environment()
    solar_array = SolarArray()
    battery_array = BatteryArray()
    panels = [SolarPanel({
            'environment': environment,
            'standard_conditions': {
                'power_rating': 100,
                'efficiency': 0.23,
                'temperature': {
                    'unit': 'Celcius',
                    'value': 25
                }
            },
            'temp_coefficient': 0.02,
            'area': 3
        }) for i in range(4)]
    batteries = [Battery(volts=12, amps=100) for battery in range(2)]
    [solar_array.add(panel) for panel in panels]
    [battery_array.add(battery) for battery in batteries]
    system = PhotoVoltaicSystem(environment=environment, panels=solar_array, batteries=battery_array)
    ACTIVE_SIMS.append(system)
    sim_time_thread = threading.Thread(target=simulated_time, args=(environment,))
    sim_time_thread.start()
    system.start()
    return { 'result': system.json() }


@app.get('/pv/system')
def pv_system(system_id: str):
    """Get PV system by _id."""
    try:
        return { 'result': get_pv_system(system_id).json() }
    except Exception as e:
        return { 'error': str(e) }


@app.get('/pv/start')
def start_pv_system(system_id: str):
    """Start target PV system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        sim_time_thread = threading.Thread(target=simulated_time, args=(system._environment,))
        sim_time_thread.start()
        system.start()
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }

    
@app.get('/pv/stop')
def stop_pv_system(system_id: str):
    """Stop target PV system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        system.stop()
        system._environment.stop()
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }


@app.get('/pv/panel')
def get_panel(system_id: str, panel_id: str):
    """Get panel data."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        panel_details = system._panels.get(panel_id)
        return { 'result': panel_details }
    except Exception as e:
        return { 'error': str(e) }


@app.get('/pv/panels')
def get_panels(system_id: str):
    """Get panels connected to a specified pv system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        return { 'result': [panel.json() for panel in system._panels] }
    except Exception as e:
        return { 'error': str(e) }


@app.post('/pv/panel/add')
def add_panel(data: IncomingSolarPanel):
    """Add panel to solar array."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(data['system_id'])
        panel = SolarPanel({
            'environment': system._environment,
            'standard_conditions': {
                'power_rating': data['stc']['power_rating'],
                'efficiency': data['stc']['efficiency'],
                'temperature': {
                    'unit': data['stc']['temperature']['unit'],
                    'value':data['stc']['temperature']['value']
                }
            },
            'temp_coefficient': data['temp_coefficient'],
            'area': data['area']
        })
        system._panels.add(panel)
        system.connect_panel_cooling(panel._id)
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }


@app.delete('/pv/panel/remove')
def remove_panel(system_id: str, panel_id: str):
    """Remove panel from target PV system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        return system._panels.remove(panel_id)
    except Exception as e:
        return { 'error': str(e) }    


@app.get('/pv/battery')
def get_battery(system_id: str, battery_id: str):
    """Get target battery details."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        battery_details = system._batteries.get(battery_id)
        return { 'result': battery_details }
    except Exception as e:
        return { 'error': str(e) }


@app.get('/pv/batteries')
def get_batteries():
    """Get batteries connected to target PV system."""
    try:
        system_id = ''
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        return { 'result': [battery.json() for battery in system._batteries] }
    except Exception as e:
        return { 'error': str(e) }


@app.post('/pv/battery/add')
def add_battery(data: IncomingBattery):
    """Add battery to target PV system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(data['system_id'])
        battery = Battery(volts=data['volts'], amps=data['amps'])
        return system._batteries.add(battery)
    except Exception as e:
        return { 'error': str(e) }


@app.delete('/pv/battery/remove')
def remove_battery(system_id: str, battery_id: str):
    """Add battery to target PV system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
        return system._batteries.remove(battery_id)
    except Exception as e:
        return { 'error': str(e) }
