"""
A collection of functions to create plots specifically for the cooler room project
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_single_type_overlayed(door_open, compressor_on, price_history, room_temperature, thermostat_type):
    """
    A visualisation of all the variables for a single thermostat type.
    """
    # Time axis (assuming all arrays are of equal length)
    time = np.arange(len(price_history))

    # Create the figure and primary axis
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot binary state heatmap (Door Open and Compressor On)
    binary_data = np.vstack([door_open, compressor_on])
    sns.heatmap(binary_data, ax=ax1, cbar=False, cmap="RdBu", xticklabels=False, yticklabels=['Door Open', 'Compressor On'],
                alpha=0.3, linewidth=0)  # Light transparency for better overlay

    ax1.set_xlabel("Time Ticks")
    ax1.set_ylabel("Binary States")
    ax1.set_title(f"{thermostat_type} thermostat: Price, Temperature & Binary States")

    # Create a secondary y-axis for price and temperature
    ax2 = ax1.twinx()

    # Plot price history and temperature history on the secondary axis
    ax2.plot(time, price_history, label="Price History", color="green", alpha=0.7, linewidth=2)
    ax2.plot(time, room_temperature, label="Room Temperature", color="blue", alpha=0.7, linewidth=2)

    ax2.set_ylabel("Price / Room Temperature")
    ax2.legend(loc="upper right")

    # Display the plot
    plt.show()

def plot_double_type_overlayed(price_history, thermostat_type, room_temperature, second_thermostat_type, second_room_temperature):
    """
    A visualisation of a comparison of room temperature in two models, in the same span as the price history.
    """
    # Time axis (assuming all arrays are of equal length)
    time = np.arange(len(price_history))

    # Create the figure and primary axis
    fig, ax1 = plt.subplots(figsize=(10, 6))


    # Plot price history and temperature history on the secondary axis
    ax1.plot(time, price_history, label="Price History", color="green", alpha=0.7, linewidth=2)

    ax1.plot(time, room_temperature, label=f"{thermostat_type} room Temperature", color="blue", alpha=0.7, linewidth=2)
    ax1.plot(time, second_room_temperature, label=f"{second_thermostat_type} room Temperature", color="red", alpha=0.7, linewidth=2)

    ax1.set_ylabel("Price / Room Temperature")
    ax1.legend(loc="upper right")

    # Display the plot
    plt.show()

def plot_boxplot(data, thermostat_type, second_data, second_thermostat_type):
    """
    A visualisation of the distribution of data in two thermostat types.
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_title(f"{thermostat_type} thermostat variance in expenses")
    ax.boxplot(data, vert=False, positions=[1])
    ax.boxplot(second_data, vert=False, positions=[2])
    ax.set_xlabel("Expenses")
    ax.set_yticks([1, 2])
    ax.set_yticklabels([thermostat_type, second_thermostat_type])
    ax.grid(True)
    plt.show()

def cumulative_sum_based_on_condition(price_history, thermostat_type, compressor_on, second_thermostat_type, second_compressor_on):
    """
    Calculate the cumulative sum of power expenses in two models.
    """
    # Ensure the arrays are the same length
    assert len(compressor_on) == len(price_history), "Arrays must be of the same length"
    assert len(second_compressor_on) == len(price_history), "Arrays must be of the same length"
    
    # Filter the prices array based on the boolean array
    #filtered_prices = price_history * compressor_on
    second_filtered_prices = price_history * compressor_on

    filtered_prices = np.where(compressor_on, price_history, 0)
    second_filtered_prices = np.where(second_compressor_on, price_history, 0)
    
    # Calculate the cumulative sum
    cumulative_sum = np.cumsum(filtered_prices)
    second_cumulative_sum = np.cumsum(second_filtered_prices)
    
    # Time axis (assuming all arrays are of equal length)
    time = np.arange(len(price_history))

    # Create the figure and primary axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot price history and temperature history on the secondary axis
    ax.plot(time, cumulative_sum, label=f"{thermostat_type} room Temperature", color="blue", alpha=0.7, linewidth=2)
    ax.plot(time, second_cumulative_sum, label=f"{second_thermostat_type} room Temperature", color="red", alpha=0.7, linewidth=2)

    ax.set_ylabel("Cumulative Price")
    ax.legend(loc="upper right")

    ax2 = ax.twinx()
    ax2.plot(time, price_history, label="Price History", color="green", alpha=0.2, linewidth=2)
    ax2.set_ylabel("Price")


    # Display the plot
    plt.show()