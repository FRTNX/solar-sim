import time
import requests

BASE_URL = 'http://localhost:8001'

test_panel = {
    'stc': {
        'power_rating': 100,
        'efficiency': 0.23,
        'temperature': {'unit': 'Celcius', 'value': 25}
    },
    'temp_coefficient': 0.1,
    'area': 3
}

test_battery = {
    'volts': 12,
    'amps': 100
}

def get_system_details(system_id: str):
    """Return PV system details."""
    response = requests.get(
        url=BASE_URL + '/pv/system',
        params={ 'system_id': system_id }
    )
    return response.json()


# todo: add assertions
if __name__ == '__main__':
    # initialise new simulation
    response = requests.get(BASE_URL + '/pv/init')
    init_response = response.json()
    print('initialisation result:', init_response)
    system_id = init_response['result']['system_id']
    
    # add solar panel
    test_panel['system_id'] = system_id
    print('adding solar panel to system:', test_panel)
    response = requests.post(BASE_URL + '/pv/panel/add', json=test_panel)
    add_panel_resp = response.json()
    print('result:', add_panel_resp)
    
    # add battery
    test_battery['system_id'] = system_id
    print('adding battery to system:', test_battery)
    response = requests.post(BASE_URL + '/pv/battery/add', json=test_battery)
    add_battery_response = response.json()
    print('result:', add_battery_response)
    
    # get system data
    print('System now looks like: ', get_system_details(system_id))
    
    # start pv system
    print('starting pv system')
    response = requests.get(BASE_URL + '/pv/start', params={ 'system_id': system_id })
    sys_start_resp = response.json()
    print('result:', sys_start_resp)
    
    # check time lapses as expected
    print('checking time simulation...')
    for i in range(20):
        print(get_system_details(system_id))
        time.sleep(2)
