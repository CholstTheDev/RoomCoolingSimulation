from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
import random

class CoolerInstance(ABC):
    def __init__(self, power_prices):
        self.tick_counter = 1

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
    
    @abstractmethod
    def evaluate_comp_on_off(self) -> float:
        """
        Method for evaluating whether the compressor should be turned on. This method varies in children.
        """
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
        
        self.already_simulated = True
        
        return np.sum(self.food_loss_expenses) + np.sum(self.power_expenses)

    def simulate_tick(self, count) -> tuple:
        """
        Logic for a 5 minute interval. 
        Calculates the current temperature, based on whether the door is open and whether the compressor is on.
        """
        door_open = self.is_door_open()
        last_temp = self.temperature_history[count-1]
        if door_open and self.evaluate_comp_on_off():
            T = last_temp + (0.0000005 * (20-last_temp) + 0.000008 * (-5 - last_temp)) * 300
            self.door_state_history[count] = True
            self.power_expenses[count] = self.power_prices[count]
            self.compressor_state_history[count] = True
        elif door_open:
            T = last_temp + (0.0000005 * (20-last_temp)) * 300
            self.power_expenses[count] = 0.0
            self.door_state_history[count] = True
            self.compressor_state_history[count] = False
        else:
            T = last_temp + (0.00003 * (20-last_temp) + 0.000008 * (-5 - last_temp)) * 300
            self.power_expenses[count] = self.power_prices[count]
            self.compressor_state_history[count] = True
            self.door_state_history[count] = False
        
        self.temperature_history[count] = T

        self.food_loss_expenses[count] = self.calculate_food_loss_expense(T)
    
    def calculate_food_loss_expense(self, temp):
        """
        Calculates the expense of food loss in a 5 minute period, at the input temperature
        """
        if temp < 3.5:
            return (4.39 * np.e)**(-0.49 * temp)
        elif temp < 6.5:
            return 0.0
        else:
            return (0.11 * np.e)**(0.31 * temp)


    

class SimpleCooler(CoolerInstance):
    def evaluate_comp_on_off(self) -> bool:
        """
        The simple cooler deciding whether to turn on the compressor.
        """
        if self.current_temperature < 5:
            return True
        else:
            return False

class ThermostatType(Enum):
    SIMPLE = SimpleCooler
