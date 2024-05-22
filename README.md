# Solar Simulator (Server)

## How To Run Current Code
### As of May 22, 2024

Assuming you have Python  3.8 (or higher) installed, first install dependencies with:
```
$ pip install -r requirements.txt
```

Then start the server with:
```
$ uvicorn main:app --port 8001
```
The port value is arbitrary; change to whichever port works best.

## Endpoints

### `GET` /pv/init

example use:
```
$ curl http://localhost:8001/pv/init
```

output:
```
{"system":{"time":"2024-05-21 00:00:00","panel_details":{"array_temparature":25.0,"total_output":0.0,"panel_details":[{"panel_id":"","power_output":0.0,"panel_temparature":25}]},"battery_details":{"voltage":600.0,"battery_details":[{"battery_id":"","type":12,"capacity":1200,"state_of_charge":0.5,"available_power":{"unit":"kilowatt","value":600.0},"voltage":6.0}]}}}
```

### `GET` /pv/start

### `GET` /pv/stop

### `GET` /pv/panel

### `POST` /pv/panel/add

### `DELETE` /pv/panel/remove

### `GET` /pv/battery

### `POST` /pv/battery/add

### `DELETE` /pv/battery/remove



