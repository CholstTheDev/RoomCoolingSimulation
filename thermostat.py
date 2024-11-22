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
    def __init__(self):
        pass

    @abstractmethod
    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        """
        Returns whether the thermostat should be on or off
        """
        pass

class SimpleThermostat(Thermostat):
    """
    Control mode: if the room temperature is above 5 degrees, turn on the compressor
    """
    def evaluate_cooler_state(self, room: "cooler_instance.CoolerInstance") -> bool:
        return room.current_temperature > 5
    
class ThermostatType(Enum):
    """
    An enumerator that returns the corresponding class
    """
    SIMPLE = SimpleThermostat