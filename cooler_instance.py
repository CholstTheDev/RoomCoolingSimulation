"""
Defines classes that handle logic related to simulating temperature changes in the cooler.
"""
import random
import math

import numpy as np

import thermostat as therm

class CoolerInstance():
    """
    Class that represents the cooler room
    """
    def __init__(self, thermostat_instance: therm.Thermostat, power_prices):
        self.tick_counter = 1

        self.thermostat_instance = thermostat_instance

        self.compressor_state_history = np.zeros(8640, dtype=bool)
        self.door_state_history = np.zeros(8640, dtype=bool)
        self.current_temperature = 5.0

        self.power_prices = power_prices

        self.temperature_history = np.zeros(8640)
        self.temperature_history[0] = self.current_temperature

        self.food_loss_expenses = np.zeros(8640)
        self.power_expenses = np.zeros(8640)

    def is_door_open(self) -> bool:
        """
        Checks if the door is open, returns true 10% of the time
        """
        if random.randint(0, 99) < 10:
            return True
        else:
            return False

    def simulate_month(self) -> float:
        """
        Simulates the coolerroom for a month, returns the total expenses
        """
        self.temperature_history[0] = 5.0

        tick_counter = 1

        while tick_counter < 8640:
            self.simulate_tick(tick_counter)
            tick_counter += 1
        return (np.sum(self.food_loss_expenses), np.sum(self.power_expenses))

    def simulate_tick(self, count) -> tuple:
        """
        Logic for a 5 minute interval. 
        Calculates the current temperature, based on whether 
        the door is open and whether the compressor is on.
        """
        last_temp = self.temperature_history[count-1] # Get the last temperature

        door_open = self.is_door_open() # Randomly decide if the door is open
        comp_on = self.thermostat_instance.evaluate_cooler_state(self) # Evaluate whether the cooler should be on

        # Decision tree looks like this for the sake of speed
        # C1 and C2's values could simply be changed by the above functions,
        # but on the scale of 1000s of simulations, it could make a difference.
        if door_open and comp_on: # If both the door is open, and the compressor is on
            t = last_temp + (0.00003 * (20-last_temp) + 0.000008 * (-5 - last_temp)) * 300 # Calculate the temperature as this
            #self.door_state_history[count] = True # Add this to the history
            #self.compressor_state_history[count] = True # And this
            self.power_expenses[count] = self.power_prices[count] # Add the price of power at this moment to the history of prices
        elif door_open:
            t = last_temp + (0.00003 * (20-last_temp)) * 300
            self.power_expenses[count] = 0.0
            #self.door_state_history[count] = True
            #self.compressor_state_history[count] = False
        elif comp_on:
            t = last_temp + (0.0000005 * (20-last_temp) + 0.000008 * (-5 - last_temp)) * 300
            self.power_expenses[count] = self.power_prices[count]
            #self.compressor_state_history[count] = True
            #self.door_state_history[count] = False
        else:
            t = last_temp + (0.0000005 * (20-last_temp)) * 300
            self.power_expenses[count] = 0.0

        self.temperature_history[count] = t # Add the temperature to the temperature history
        self.current_temperature = t # Set the current temperature to the new calculated temperature

        self.food_loss_expenses[count] = self.calculate_food_loss_expense(t) # Calculate and add the price of food loss for this tick

    def calculate_food_loss_expense(self, temp):
        """
        Calculates the expense of food loss in a 5 minute period, at the input temperature
        """
        if temp < 3.5:
            return 4.39 * math.exp(-0.49 * temp)
        elif temp < 6.5:
            return 0.0
        else:
            return 0.11 * math.exp(0.31 * temp)
