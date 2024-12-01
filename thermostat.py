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
    def __init__(self):
        pass

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
        return room.current_temperature > 5

class OpportunistThermostat(Thermostat):
    """
    More likely to keep cooling when the price is low. Doesn't cool below 3.5 degrees.
    Turns on no matter what when temperature exceeds a threshold.
    """
    def __init__(self):
        self.price_threshold = 2


    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        if room.current_temperature > 6.3:
            return True
        elif room.current_temperature < 3.5:
            return False
        
        if room.power_prices[room.tick_counter] < self.price_threshold:
            #print(f"Bargain! {room.power_prices[room.tick_counter]}")
            return True
        else:
            return False


class DesperationThermostat(Thermostat):
    """
    This thermostat gets desperate when when the temperature becomes too high, and becomes more willing to buy expensive power.
    """
    def __init__(self):
        self.lowest_temperature = 3.5
        self.highest_temperature = 6.375

        self.lowest_price = 0.015
        self.highest_price = 4 #Max value in set: 5.429 

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        price_point = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * (self.highest_price - self.lowest_price) + self.lowest_price
        return room.power_prices[room.tick_counter] <= price_point

class DesperationOpportunistThermostat(Thermostat):
    """
    This thermostat mixes the DESPERATION thermostat and the OPPORTUNIST thermostat.
    """
    def __init__(self):
        self.lowest_temperature = 3.5
        self.highest_temperature = 6.375

        self.lowest_price = 0.015
        self.highest_price = 3 #Max value in set: 5.429 

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        if room.current_temperature > 6.375:
            return True
        elif room.current_temperature < 3.5:
            return False
        
        price_point = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature) * (self.highest_price - self.lowest_price) + self.lowest_price
        
        if room.power_prices[room.tick_counter] < 0.5:
            return True
        else:
            return room.power_prices[room.tick_counter] < price_point

class PeerReviewThermostat(Thermostat):
    """
    This thermostat that buys if it is the lowest in the group of prices around it
    """
    def __init__(self):
        self.look_around = 245

    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        if room.current_temperature > 6.34:
            return True
        elif room.current_temperature < 3.5:
            return False
        low_check = max(0, room.tick_counter - self.look_around)
        hich_check = min(8640, room.tick_counter + self.look_around)
        average_peer_prices = np.mean(room.power_prices[low_check:hich_check])
        current_price = room.power_prices[room.tick_counter]        
        if current_price < average_peer_prices:
            return True
        return False

class PartitionThermostat(Thermostat):
    """
    Buys all the cheapest power, within the partition. If partitio_count = 10, it will buy the cheapest x amount of power
    """
    def __init__(self):
        self.partition_count = 50
        self.partition_size = 8640 / self.partition_count

        self.purchase_per_partition =60

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

class DesperationExponentialThermostat(Thermostat):
    """
    Desperation opportunist with an exponential twist
    """
    def __init__(self):
        self.lowest_temperature = 3.5
        self.highest_temperature = 6

        self.lowest_price = 0.015
        self.highest_price = 5.429 

        self.b = 5.891460032803241 # b = np.log(5.429/0.015)
        self.steepness = 0.8


    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        if room.current_temperature > self.highest_temperature:
            return True
        elif room.current_temperature < self.lowest_temperature:
            return False
        
        desperation_value = (room.current_temperature - self.lowest_temperature) / (self.highest_temperature - self.lowest_temperature)
        price_point = self.lowest_price * np.exp(self.b * self.steepness * desperation_value)
        current_price = room.power_prices[room.tick_counter]

        return current_price <= price_point


class ThermostatType(Enum):
    """
    An enumerator that returns the corresponding class
    """
    SIMPLE = SimpleThermostat
    OPPORTUNIST = OpportunistThermostat
    DESPERATION = DesperationThermostat
    DESPERATION_OPPORTUNIST = DesperationOpportunistThermostat
    PEERREVIEW = PeerReviewThermostat
    PARTITION = PartitionThermostat
    DESPERATION_EXPONENTIAL = DesperationExponentialThermostat

