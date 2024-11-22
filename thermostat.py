"""
Holds the abstract class "thermostats", from which all thermostat types inherit.
"""
from enum import Enum
from abc import ABC, abstractmethod
import math

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
        return room.current_temperature >= self.highest_allowed_temp

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
        self.highest_temperature = 6.375

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
        self.highest_temperature = 6.375

        self.lowest_price = 0.015
        self.highest_price = 3 #Max value in set: 5.429 

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        price_point = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * (self.highest_price - self.lowest_price) + self.lowest_price
        
        if (room.power_prices[room.tick_counter] < 0.5 and room.current_temperature > self.lowest_temperature):
            return True
        elif room.current_temperature > 6.375:
            return True
        else:
            return room.power_prices[room.tick_counter] < price_point

class WatcherThermostat(Thermostat):
    """
    This thermostat mixes the DESPERATION thermostat and the OPPORTUNIST thermostat
    """
    def __init__(self, config: dict):
        self.config = config

        self.lowest_temperature = 3.5
        self.highest_temperature = 6.5

        self.look_around = 5
        self.max_diff = 0.06

        self.lowest_price = 0.015
        self.highest_price = 3 #Max value in set: 5.429 

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        #desperation_value = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * 2
        if room.current_temperature > 6.375:
            return True
        
        current_price = room.power_prices[room.tick_counter]
        price_point = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * (self.highest_price - self.lowest_price) + self.lowest_price
        average_next_prices = np.average(room.power_prices[room.tick_counter:room.tick_counter + self.look_around])
        average_previous_prices = np.average(room.power_prices[room.tick_counter - self.look_around:room.tick_counter])
        diff = average_next_prices - average_previous_prices
        
        
        if average_next_prices > current_price and average_previous_prices > current_price:
            print("I am at a hole!")
            print(f"diff: {diff}")
            return True
        
        if room.power_prices[room.tick_counter] < price_point and room.current_temperature > 3.5:
            #print(f"Bargain! {room.power_prices[room.tick_counter]}")
            return True
        
        return False

class PeerReviewThermostat(Thermostat):
    """
    This thermostat mixes the DESPERATION thermostat and the OPPORTUNIST thermostat
    """
    def __init__(self, config: dict):
        self.config = config

        self.lowest_temperature = 3.5
        self.highest_temperature = 6.375

        self.look_around = 5
        self.max_diff = 0.06

        self.lowest_price = 0.015
        self.highest_price = 2.5 #Max value in set: 5.429 

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        #desperation_value = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * 2
        if room.current_temperature > 6.3:
            return True
        average_peer_prices = np.average(room.power_prices[room.tick_counter - self.look_around:room.tick_counter + self.look_around])
        current_price = room.power_prices[room.tick_counter]
        price_point = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * (self.highest_price - self.lowest_price) + self.lowest_price
        average_next_prices = np.average(room.power_prices[room.tick_counter:room.tick_counter + self.look_around])
        average_previous_prices = np.average(room.power_prices[room.tick_counter - self.look_around:room.tick_counter])
        diff = average_next_prices - average_previous_prices
        
        if current_price < average_peer_prices and room.current_temperature > 3.5:
            return True
        elif current_price < price_point:
            return True
        return False
        
        if average_next_prices > current_price and average_previous_prices > current_price:
            print("I am at a hole!")
            print(f"diff: {diff}")
            return True
        
        if room.power_prices[room.tick_counter] < price_point and room.current_temperature > 3.5:
            #print(f"Bargain! {room.power_prices[room.tick_counter]}")
            return True
        
        return False

class PartitionThermostat(Thermostat):
    """
    Buys all the cheapest power, within the partition
    """
    def __init__(self, config: dict):
        self.config = config

        self.partition_count = 10
        self.partition_size = 8640 / self.partition_count

        self.purchase_per_partition =350

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        if room.current_temperature > 6.2:
            return True
        elif room.current_temperature < 3.6:
            return False
        #Calculate partition start and end as integers
        partition_start = int((room.tick_counter // self.partition_size) * self.partition_size)
        partition_end = int(partition_start + self.partition_size)

        # Safeguard: Adjust the slice range to avoid out-of-bounds
        partition_end = min(partition_end, len(room.power_prices))

        # Extract the sliced array for the current partition
        partition_sliced_array = room.power_prices[partition_start:partition_end]

        # Handle case where the partition is smaller than expected
        if len(partition_sliced_array) < self.purchase_per_partition:
            return False  # Not enough data to evaluate

        # Find the lowest purchase_per_partition prices in the current partition
        lowest_prices = np.partition(partition_sliced_array, self.purchase_per_partition)[:self.purchase_per_partition]
        current_price = room.power_prices[room.tick_counter]

        # Compare the current price to the threshold
        if current_price <= lowest_prices[self.purchase_per_partition - 1]:
            return True

        return False



class ThermostatType(Enum):
    """
    An enumerator that returns the corresponding class
    """
    SIMPLE = SimpleThermostat
    OPPORTUNIST = OpportunistThermostat
    BARGAIN = BargainThermostat
    DESPERATION = DesperationThermostat
    DESPERATION_OPPORTUNIST = DesperationOpportunistThermostat
    WATCHER = WatcherThermostat
    PEERREVIEW = PeerReviewThermostat
    PARTITION = PartitionThermostat

