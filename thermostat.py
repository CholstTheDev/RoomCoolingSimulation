"""
Holds the abstract class "thermostats", from which all thermostat types inherit.
"""
from enum import Enum
from abc import ABC, abstractmethod

import numpy as np

import cooler_instance



class Thermostat(ABC):
    """
    Thermostat base class.
    """
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        """
        Returns whether the thermostat should be on or off
        """
class SimpleThermostat(Thermostat):
    """
    Control mode: if the room temperature is above 5 degrees, turn on the compressor
    """

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        return room.current_temperature > self.config["SIMPLE"]["TEMP"]

class OpportunistThermostat(Thermostat):
    """
    More likely to keep cooling when the price is low. Doesn't cool below 3.5 degrees.
    Turns on no matter what when temperature exceeds a threshold.
    """
    def __init__(self, config: dict):
        self.config = config
        self.price_threshold = self.config["OPPORTUNIST"]["PRICE_OPPORTUNITY_THRESHOLD"]
        self.highest_allowed_temp = self.config["OPPORTUNIST"]["HIGH_TEMP"]
        self.lowest_allowed_temp = self.config["OPPORTUNIST"]["LOW_TEMP"]


    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        if room.power_prices[room.tick_counter] < self.price_threshold and room.current_temperature > self.lowest_allowed_temp:
            #print(f"Bargain! {room.power_prices[room.tick_counter]}")
            return True
        return room.current_temperature > self.highest_allowed_temp

class BargainThermostat(Thermostat):
    """
    This thermostat loves cheap energy, always turns on when it is cheap
    """
    def __init__(self, config: dict):
        self.config = config
        self.price_threshold = self.config["BARGAIN"]["PRICE_THRESHOLD"]

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        return room.power_prices[room.tick_counter] < self.price_threshold

class DesperationThermostat(Thermostat):
    """
    This thermostat gets desperate when when the temperature becomes too high, and becomes more willing to buy expensive power
    """
    def __init__(self, config: dict):
        self.config = config

        self.lowest_temperature = 3.5
        self.highest_temperature = 6.3

        self.lowest_price = 0.015
        self.highest_price = 3 #Max value in set: 5.429 

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        price_point = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * (self.highest_price - self.lowest_price) + self.lowest_price
        return room.power_prices[room.tick_counter] < price_point

class DesperationOpportunistThermostat(Thermostat):
    """
    This thermostat mixes the DESPERATION thermostat and the OPPORTUNIST thermostat
    """
    def __init__(self, config: dict):
        self.config = config

        self.lowest_temperature = 3.5
        self.highest_temperature = 6.3

        self.lowest_price = 0.015
        self.highest_price = 3 #Max value in set: 5.429 

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        price_point = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * (self.highest_price - self.lowest_price) + self.lowest_price
        
        if (room.power_prices[room.tick_counter] < 0.5 and room.current_temperature > self.lowest_temperature):
            return True
        elif room.current_temperature > 6.3:
            return True
        else:
            return room.power_prices[room.tick_counter] < price_point


class ThermostatType(Enum):
    """
    An enumerator that returns the corresponding class
    """
    SIMPLE = SimpleThermostat
    OPPORTUNIST = OpportunistThermostat
    BARGAIN = BargainThermostat
    DESPERATION = DesperationThermostat
    DESPERATION_OPPORTUNIST = DesperationOpportunistThermostat

