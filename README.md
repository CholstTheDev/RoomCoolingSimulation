# RoomCoolingSimulation
A school project about controlling a room cooling thermostat

# How to run
I suggest opening it in a virtual environment (venv). A virtual environment lets you install packages locally, without having to install them on your system. Here's how to make a venv:

## Windows:
In your VS Code terminal (or another terminal), run these commands (make sure you are in the project directory):

```sh
python -m venv venv # makes the virtual environment (venv)
.\venv\Scripts\activate # activates the virtual environment (venv)
pip install -r requirements.txt
```

## Linux:
In your terminal, run these commands in the project directory:

```sh
python -m venv venv # makes the virtual environment (venv)
source venv/bin/activate # activates the virtual environment (venv)
pip install -r requirements.txt
```

# How to use the program
There is no gui or command-line instructions. Instead, I opted for a config, to decide what to run. This is `config.yaml`. Simply change the values, to change what the simulation runs.