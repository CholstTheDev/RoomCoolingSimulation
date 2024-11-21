"""
This program runs a simulation
"""
import yaml
import doctest
import CoolerClasses as cc
import numpy as np

def load_config() -> dict:
    """
    Loads the config
    """
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            return config
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")


def load_power_prices() -> np.array:
    try:
        return np.genfromtxt("elpris.csv", skip_header=1, usecols=1, dtype=float, delimiter=',')
    except np.errstate as e:
        print(f"Error reading CSV: {e}")

def instantiate_from_enum(enum_value: str, config, power_prices) -> cc.CoolerInstance:
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
    cooler = instantiate_from_enum(config["ThermoType"], config, power_prices)
    #cooler = cc.ThermostatType.config["ThermoType"](config, power_prices)

    expense = cooler.simulate_month()
    print(f"Expenses for the month: {expense}")



