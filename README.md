# Solar Simulator (Server)

[![Solar simulator UI](src/assets/images/solar-sim.png?raw=true "Solar Simulator")](https://github.com/FRTNX/solar-sim/blob/master/src/assets/images/solar-sim.png)

Live demo: https://solar-ui.vercel.app

## How To Run Current Code
### As of June 6, 2024

* If you're on Linux ignore the fnm related commands and just ensure you have Nodejs 18+ and Python 3.10+ installed.

#### Getting the Code

First clone the server code by running the following on a Linux terminal or Windows PowerShell:
```
$ git clone https://github.com/FRTNX/solar-sim
```

Then clone the client code with:
```
git clone https://github.com/FRTNX/solar-ui
```

#### Client Setup

Specifications
 * Node.js version 18.13.0 (or higher)
 * npm 8.19.3

Setting up the client typically requires just two commands, but on Windows this can be tricky due to `npm` environment variables not being set automatically. Nevertheless, below is a walk through on how to get it done.

First, move to the client code's directory with:
```
cd solar-ui
```

Then check that npm is installed correctly with:
```
npm --version
```

If you're on Windows and `npm` isn't recognised even though you've previously installed it, check that the fnm environment variables are set correctly with:
```
fnm env
```
If the output of the above command is multiple lines starting with the keyword `SET`, copy all the output starting with `SET` by marking it all and pressing Ctrl+C, then paste it into the terminal and press enter. Now verifyy that the `npm` command works with:
```
npm --version
```

Once that's done, simply install the client dependencies with:
```
npm install
```

Then start the client with:
```
npm run dev
```

And just like that, the client should be ready to go!

#### Server Setup

Specifications:
* Python 3.10.4 (or higher)
* pip 23.1.2 (or higher)

Setting up the server is simple, as Windows does a good job on setting Python environment variables.

Open a new terminal/PowerShell window, then move the server code's directory with:
```
cd solar-sim
```

Install requirements:
```
pip install -r requirements.txt
```

Move to the `src` directory with:
```
cd src
```

Then finally, run the server with
```
uvicorn main:app --port 8001
```

And thats it!

To access the simulator, open your browser and visit http://localhost:5173


### Updating Existing Code

When the code is updated on github, you can merge in new changes by navigating to either the `solar-sim` or `solar-ui` directory and running:
```
git pull
```
Assuming you haven't modified the code on your machine, this command will seamlessly integrate new changes. If you've modified the local code base then merging in new changes may become a little more complicated, so much so that you'd be better off deleting/moving your current `solar-sim` and `solar-ui` directories and following these instructions from the start. However, it is much simpler if you are familiar with git merging.

### API Swagger Documentation

Swagger documentation is available for the API at:

`http://localhost:8001/docs`

### API Tests

To run API tests, open the solar-sim `src` directory and run:
```
python pv_api_tests.py
```
