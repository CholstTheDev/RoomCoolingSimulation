"""
Main program. This program runs a simulation
"""
import yaml
import time

import numpy as np

import cooler_instance as ci
import thermostat as therm
import visualisation as vis

def load_config(path: str) -> dict:
    """
    Reads the config from given path

    >>> load_config("test.yaml")
    {'setting1': 'value1', 'setting2': 'value2'}
    """
    try:
        with open(path, "r", encoding="utf=8") as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")


def load_power_prices(path: str) -> np.array:
    """
    Reads the power price history from the given path

    >>> np.savetxt("test_prices.csv", np.array([[0, 10.0], [1, 20.0], [2, 30.0]]), delimiter=',', header='Time,Price', comments='')
    >>> load_power_prices("test_prices.csv")
    array([10., 20.])
    """
    try:
        return np.genfromtxt(path, skip_header=1, skip_footer=1, usecols=1, dtype=float, delimiter=',')
    except (OSError, ValueError) as e:
        print(f"Error reading CSV: {e}")

def instantiate_thermostat_from_enum(enum_value: str) -> therm.Thermostat:
    """
    Points a string to a class definition.

    >>> instantiate_thermostat_from_enum("SIMPLE")
    <class 'thermostat.SimpleThermostat'>
    """
    try:
        # Get the Enum member by the string and get the associated class
        thermostat_class = therm.ThermostatType[enum_value].value
        return thermostat_class
    except KeyError as exc:
        raise ValueError(f"Invalid ThermostatType: {enum_value}") from exc

def simulate_multiple_months(target_cooler, simulation_steps: int) -> tuple:
    food_expenses_per_month = np.zeros(simulation_steps, dtype=float)
    power_expenses_per_month = np.zeros(simulation_steps, dtype=float)
    
    counter = 0
    while counter < simulation_steps:
        values = target_cooler.simulate_month(False)
        food_expenses_per_month[counter] = values[0]
        power_expenses_per_month[counter] = values[1]
        counter += 1
    
    return food_expenses_per_month, power_expenses_per_month

def run_simulation():
    print("Reading config from config.yaml...")
    config = load_config("config.yaml") # Loads 'config.yaml'

    print("Reading power prices...")
    power_prices = load_power_prices("elpris.csv")

    print("Instantiating classes...")
    thermostat = instantiate_thermostat_from_enum(config["thermostat_type"])()
    cooler = ci.CoolerInstance(thermostat, power_prices)
    if config["comparison_simulation"]:
        second_thermostat = instantiate_thermostat_from_enum(config["second_thermostat_type"])()
        second_cooler = ci.CoolerInstance(second_thermostat, power_prices)

    if config["simulate_multiple_months"]:
        if config["comparison_simulation"]:
            start_time = time.time()
            print(f"Running first simulation for {config['simulation_steps']} steps (months)...")
            food_expenses_per_month, power_expenses_per_month = simulate_multiple_months(cooler, config["simulation_steps"])
            print(f"Running second simulation for {config['simulation_steps']} steps (months)...")
            second_food_expenses_per_month, second_power_expenses_per_month = simulate_multiple_months(second_cooler, config["simulation_steps"])
            elapsed_time = time.time() - start_time
            print(f"Finished. Took {round(elapsed_time, 2)} seconds")

            vis.plot_boxplot(food_expenses_per_month + power_expenses_per_month, config["thermostat_type"], second_food_expenses_per_month + second_power_expenses_per_month, config["second_thermostat_type"])

        else:
            print(f"Running simulation for {config['simulation_steps']} steps (months)...")
            start_time = time.time()
            food_expenses_per_month, power_expenses_per_month = simulate_multiple_months(cooler, config["simulation_steps"])
            elapsed_time = time.time() - start_time

            print(f"Average food expense over {config['simulation_steps']} months: {int(np.mean(food_expenses_per_month))} kr.")
            print(f"Average power expense over {config['simulation_steps']} months: {int(np.mean(power_expenses_per_month))} kr. ")
            print(f"Thermostat type: {config['thermostat_type']}")
            print(f"Took {round(elapsed_time, 2)} seconds")
    else:
        # values: 0 = food expenses, 1 = power expenses, 2 = temperature history, 3 = door state history, 4 = compressor state history
        print("Running simulation once...")
        start_time = time.time()
        
        if config["comparison_simulation"]:
            values = cooler.simulate_month(True)
            second_values = second_cooler.simulate_month(True)
            elapsed_time = time.time() - start_time
            vis.plot_double_type_overlayed(power_prices, config["thermostat_type"], values[2], config["second_thermostat_type"], second_values[2])
            vis.cumulative_sum_based_on_condition(power_prices, config["thermostat_type"], values[4], config["second_thermostat_type"], second_values[4])
            print(f"Thermostat type: {config['thermostat_type']}, expenses: {str(np.sum(values[0]) + np.sum(values[1]))} kr.")
            print(f"Second thermostat type: {config['second_thermostat_type']}, expenses: {str(np.sum(second_values[0]) + np.sum(second_values[1]))} kr.")
        else:
            values = cooler.simulate_month(True)
            elapsed_time = time.time() - start_time

            print(f"Food expense for the month: {int(np.sum(values[0]))} kr.")
            print(f"Power expense for the month: {int(np.sum(values[1]))} kr.")
            vis.plot_single_type_overlayed(values[3], values[4], power_prices, values[2], config["thermostat_type"]) #[0:8640//2]
            print(f"Thermostat type: {config['thermostat_type']}")
            print(f"Took {round(elapsed_time, 2)} seconds")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("Doctest successful")

run_simulation()