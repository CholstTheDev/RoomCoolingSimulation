"""
This program runs a simulation
"""
import yaml
import doctest
import CoolerClasses as cc
import numpy as np

def load_config() -> dict:
    """
    Reads the config from
    """
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            return config
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")


def load_power_prices() -> np.array:
    """
    Reads the power price history from 'elpris.csv'
    """
    try:
        return np.genfromtxt("elpris.csv", skip_header=1, usecols=1, dtype=float, delimiter=',')
    except np.errstate as e:
        print(f"Error reading CSV: {e}")

def instantiate_from_enum(enum_value: str, config, power_prices) -> cc.CoolerInstance:
    """
    Points a string to a class definition.
    """
    try:
        # Get the Enum member by the string and get the associated class
        thermostat_class = cc.ThermostatType[enum_value].value
        return thermostat_class(config, power_prices)
    except KeyError:
        raise ValueError(f"Invalid ThermostatType: {enum_value}")

if __name__ == "__main__":
    """
    If this script is named main, run this.
    """
    print("Reading config from config.yaml...")
    config = load_config() # Loads 'config.yaml'
    print("Reading power prices...")
    power_prices = load_power_prices()

    print("Instantiating class...")
    cooler = instantiate_from_enum(config["Thermostat type"], config, power_prices)
    #cooler = cc.ThermostatType.config["ThermoType"](config, power_prices)

    expenses_per_month = np.zeros(config["Simulation steps"], dtype=float)
    counter = 0
    while counter < config["Simulation steps"]:
        expenses_per_month[counter] = cooler.simulate_month()
        counter += 1

    print(np.average(expenses_per_month))
    #print(f"Average expense over {config["Simulation steps"]} months: {np.average(expenses_per_month)} \n Thermostat type: {config['Thermostat type']}")



