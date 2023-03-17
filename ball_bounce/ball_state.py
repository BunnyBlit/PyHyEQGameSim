"""A bouncing ball state! As a list serializable class
"""
from dataclasses import dataclass
from typing import List
from collections.abc import Sequence

@dataclass(init=False)
class BallState(Sequence):
    """State of a bouncing ball! We only care about one dimension,
        we're not worried about left/right position for a demo
    Properties:
        y_pos (float): y position
        y_vel (float): y velocity
    """
    _data: List[float]

    def __init__(self, y_pos:float, y_vel:float):
        self._data = [0.0, 0.0] # initialize the array
        self.y_pos=y_pos
        self.y_vel=y_vel

    @property
    def y_pos(self) -> float:
        return self._data[0]

    @y_pos.setter
    def y_pos(self, value:float):
        self._data[0] = value

    @property
    def y_vel(self) -> float:
        return self._data[1]

    @y_vel.setter
    def y_vel(self, value:float):
        self._data[1] = value

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key:int) -> float:
        return self._data[key]
