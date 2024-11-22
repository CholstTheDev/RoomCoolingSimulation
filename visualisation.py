"""
A collection of functions to create plots specifically for the cooler room project
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_test(door_open, compressor_on, price_history, room_temperature):
    """
    A visualisation of all the variables. Made with ChatGPT.
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
    ax1.set_title("Overlayed Time-Series: Price, Temperature & Binary States")

    # Create a secondary y-axis for price and temperature
    ax2 = ax1.twinx()

    # Plot price history and temperature history on the secondary axis
    ax2.plot(time, price_history, label="Price History", color="green", alpha=0.7, linewidth=2)
    ax2.plot(time, room_temperature, label="Room Temperature", color="blue", alpha=0.7, linewidth=2)

    ax2.set_ylabel("Price / Room Temperature")
    ax2.legend(loc="upper right")

    # Display the plot
    plt.show()
