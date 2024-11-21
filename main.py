"""
This program runs a simulation
"""
import doctest
import yaml

import numpy as np

import cooler_instance as cc

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

def instantiate_from_enum(enum_value: str) -> cc.CoolerInstance:
    """
    Points a string to a class definition.
    """
    try:
        # Get the Enum member by the string and get the associated class
        thermostat_class = cc.ThermostatType[enum_value].value
        return thermostat_class
    except KeyError as exc:
        raise ValueError(f"Invalid ThermostatType: {enum_value}") from exc

if __name__ == "__main__":
    print("Reading config from config.yaml...")
    config = load_config() # Loads 'config.yaml'
    print("Reading power prices...")
    power_prices = load_power_prices()

    print("Instantiating class...")
    cooler = instantiate_from_enum(config["Thermostat type"])(power_prices)

    print(f"Running simulation for {config['Simulation steps']} steps (months)...")
    expenses_per_month = np.zeros(config["Simulation steps"], dtype=float)
    counter = 0
    while counter < config["Simulation steps"]:
        expenses_per_month[counter] = cooler.simulate_month()
        counter += 1

    print(f"Average expense over {config['Simulation steps']} months: {int(np.average(expenses_per_month))} kr. \n Thermostat type: {config['Thermostat type']}")
