""" Dataclass to hold onto hybrid running state! Hybrid points
    map a state to a time, along with the number of jumps to get there
"""

from dataclasses import dataclass
from typing import Generic, TypeVar
from collections.abc import Sequence
from .ndarray_dataclass import NDArrayBacked


T = TypeVar("T", bound=NDArrayBacked)


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

    def to_simple(self):
        return (self.time, self.state.to_simple(), self.jumps)
    def __str__(self):
        return f"{self.time:0.4f}\t{self.state}\t{self.jumps}"
