"""
This program runs a simulation
"""
import doctest
import yaml
import time

import numpy as np

import cooler_instance as ci
import thermostat as therm
#import visualisation as vis

def load_config() -> dict:
    """
    Reads the config from config.yaml
    """
    try:
        with open("config.yaml", "r", encoding="utf=8") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")


def load_power_prices() -> np.array:
    """
    Reads the power price history from 'elpris.csv'
    """
    try:
        return np.genfromtxt("elpris.csv", skip_header=1, usecols=1, dtype=float, delimiter=',')
    except (OSError, ValueError) as e:
        print(f"Error reading CSV: {e}")

def instantiate_thermostat_from_enum(enum_value: str) -> therm.Thermostat:
    """
    Points a string to a class definition.
    """
    try:
        # Get the Enum member by the string and get the associated class
        thermostat_class = therm.ThermostatType[enum_value].value
        return thermostat_class
    except KeyError as exc:
        raise ValueError(f"Invalid ThermostatType: {enum_value}") from exc

if __name__ == "__main__":
    print("Reading config from config.yaml...")
    config = load_config() # Loads 'config.yaml'
    print("Reading power prices...")
    power_prices = load_power_prices()

    print("Instantiating classes...")
    thermostat = instantiate_thermostat_from_enum(config["Thermostat type"])(config)
    cooler = ci.CoolerInstance(thermostat, power_prices)

    print(f"Running simulation for {config['Simulation steps']} steps (months)...")
    food_expenses_per_month = np.zeros(config["Simulation steps"], dtype=float)
    power_expenses_per_month = np.zeros(config["Simulation steps"], dtype=float)
    start_time = time.time()
    counter = 0
    while counter < config["Simulation steps"]:
        values = cooler.simulate_month()
        food_expenses_per_month[counter] = values[0]
        power_expenses_per_month[counter] = values[1]
        counter += 1
    elapsed_time = time.time() - start_time

    print(f"Average food expense over {config['Simulation steps']} months: {int(np.average(food_expenses_per_month))} kr.")
    print(f"Average power expense over {config['Simulation steps']} months: {int(np.average(power_expenses_per_month))} kr. ")
    print(f"Thermostat type: {config['Thermostat type']}")
    print(f"Took {elapsed_time.__round__(2)} seconds")
