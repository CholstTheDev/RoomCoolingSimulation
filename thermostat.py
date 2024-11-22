"""
Holds the abstract class "thermostats", from which all thermostat types inherit.
"""
from enum import Enum
from abc import ABC, abstractmethod

import cooler_instance



class Thermostat(ABC):
    """
    Thermostat base class.
    """
    @abstractmethod
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
        

class ThermostatType(Enum):
    """
    An enumerator that returns the corresponding class
    """
    SIMPLE = SimpleThermostat
    OPPORTUNIST = OpportunistThermostat
    BARGAIN = BargainThermostat

