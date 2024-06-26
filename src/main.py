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

environment = Environment()

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

ACTIVE_SIMULATIONS: List[PhotoVoltaicSystem] = []


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
    
class CoolingSystemUpdate(TypedDict):
    system_id: str
    active: bool

class ClientMetadata(TypedDict):
    system_id: str
    system: int
    inverter: int
    panels: dict
    batteries: dict
    cooling_systems: dict
    
class SystemDetails(TypedDict):
    system_id: str

class IncomingIterations(TypedDict):
    system_id: str
    value: int

@freeze_time('May 21, 2024 04:00', auto_tick_seconds=300)
def simulated_time(environment: Environment):
    """Updates an environment's time value based on specified interval."""
    while environment._active:
        environment.set_time(datetime.now())
        time.sleep(1)

sim_time_thread = threading.Thread(target=simulated_time, args=(environment,))
sim_time_thread.start()

def get_pv_system(system_id: str):
    """Get PhotoVoltaicSystem by _id."""
    for system in ACTIVE_SIMULATIONS:
        if system._id == system_id:
            return system
    raise ValueError('PVS_NOT_FOUND')

@app.get('/pv/init')
def create_env():
    solar_array = SolarArray()                     # create empty solar array
    battery_array = BatteryArray()                 # create empty battery array
    system = PhotoVoltaicSystem(environment=environment, panels=solar_array, batteries=battery_array)
    ACTIVE_SIMULATIONS.append(system)
    return { 'result': system.json() }

@app.get('/pv/init/default')
def create_default_sim():
    """Initialise and start default simulation."""
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
    ACTIVE_SIMULATIONS.append(system)
    system.start()
    return { 'result': system.json() }

# todo: switch back to get, system id to query param
@app.put('/pv/system')   # method changed from get to put to support request body
def pv_system(data: SystemDetails):
    """Get PV system by _id."""
    try:
        return { 'result': get_pv_system(data['system_id']).json() }
    except Exception as e:
        return { 'error': str(e) }

@app.get('/pv/system/data')
def system_data(system_id: str, target_data: str):
    """Get system time series."""
    try:
        if target_data == 'system':
            return { 'result': get_pv_system(system_id).system_data() }
        elif target_data == 'panels':
            return { 'result': get_pv_system(system_id).panel_data() }
        elif target_data == 'batteries':
            return { 'result': get_pv_system(system_id).battery_data() }
        elif target_data == 'inverter':
            return { 'result': get_pv_system(system_id).inverter_data() }
        elif target_data =='cooling':
            return { 'result': get_pv_system(system_id).cooling_data() }
        elif target_data == 'iter':
            return { 'result': get_pv_system(system_id).get_iterations() }
        else:
            return { 'result': get_pv_system(system_id).json() }
    except Exception as e:
        return { 'error': str(e) } 

@app.put('/pv/system/iterations')
def pv_iterations(data: IncomingIterations):
    try:
        system = get_pv_system(data['system_id'])
        system.set_max_iteration(data['value'])
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }

@app.get('/pv/start')
def start_pv_system(system_id: str):
    """Start target PV system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(system_id)
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

@app.put('/pv/panel/add')
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
        if system._metadata:
            system._metadata['panels'][panel._id] = 0             # update metadata
            system._metadata['cooling_systems'][panel._id] = 0
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

@app.put('/pv/battery/add')
def add_battery(data: IncomingBattery):
    """Add battery to target PV system."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(data['system_id'])
        battery = Battery(volts=data['volts'], amps=data['amps'])
        if system._metadata:
            system._metadata['batteries'][battery._id] = 0
            print('post battery meta:', system._metadata)
        system._batteries.add(battery)
        return { 'result': 'SUCCESS' }
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

@app.put('/pv/cooling/update')
def update_cooling_system(data: CoolingSystemUpdate):
    """Turn a cooling system on or off."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(data['system_id'])
        if data['active'] == True:
            system.activate_panel_cooling()
        if data['active'] == False:
            system.deactivate_panel_cooling()
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }

@app.put('/pv/metadata/update')
def update_metadata(data: ClientMetadata):
    """Capture the last recieved data from the client."""
    try:
        system: PhotoVoltaicSystem = get_pv_system(data['system_id'])
        system.update_metadata(data)
        return { 'result': 'SUCCESS' }
    except Exception as e:
        return { 'error': str(e) }
