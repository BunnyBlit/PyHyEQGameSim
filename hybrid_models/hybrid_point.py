""" Dataclass to hold onto hybrid running state! Hybrid points
    map a state to a time, along with the number of jumps to get there
"""

from dataclasses import dataclass
from typing import Generic, TypeVar
from collections.abc import Sequence

T = TypeVar("T", bound=Sequence)


@dataclass
class HybridPoint(Generic[T]):
    """A single point in a hybrid solution! A full hybrid solution
        is a sequence of some kind of these
    Attributes:
        time (float): time when this state happened
        state (T): state at this time and number of jumps
        jumps (int): number of jumps that happened before this state
    """
    time: float
    state: T
    jumps: int
