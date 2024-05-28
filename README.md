# Solar Simulator (Server)

[![Solar simulator UI](src/assets/images/solar-sim.png?raw=true "Solar Simulator")](https://github.com/FRTNX/solar-sim/blob/master/src/assets/images/solar-sim.png)

Live demo: https://solar-ui.vercel.app

## How To Run Current Code
### As of May 28, 2024

Assuming you have Python  3.8 (or higher) installed, first install dependencies with:
```
$ pip install -r requirements.txt
```

Then start the server with:
```
$ uvicorn main:app --port 8001
```
The port value is arbitrary; change to whichever port works best.

### API Swagger Documentation

Swagger documentation is available for the API at:

`http://localhost:8001/docs`

### API Tests

To run API tests, open the `src` directory and run:
```
$ python pv_api_tests.py
```
