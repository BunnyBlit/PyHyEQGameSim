""" Flappy state! As a list serializable class
"""
from dataclasses import dataclass
from typing import List, Any, Union, Iterator
from hybrid_models.ndarray_dataclass import NDArrayBacked
from collections.abc import Sequence

class FlappyState(NDArrayBacked[float | int]):
    """ State of Flappy the bird! Changes over solve time.
    Properties:
        x_pos (float): x position
        y_pos (float): y position
        y_vel (float): y velocity.
                       x_vel is constant and doesn't need to be part of state.
        pressed (int): if the button is pressed or not
    """

    @property
    def x_pos(self) -> float:
        return self._data[0]
    
    @x_pos.setter
    def x_pos(self, value:float):
        self._data[0] = value

    @property
    def y_pos(self) -> float:
        return self._data[1]
    
    @y_pos.setter
    def y_pos(self, value:float):
        self._data[1] = value

    @property
    def y_vel(self) -> float:
        return self._data[2]
    
    @y_vel.setter
    def y_vel(self, value:float):
        self._data[2] = value

    @property
    def pressed(self) -> int:
        return self._data[3]
    
    @pressed.setter
    def pressed(self, value:int):
        self._data[3] = value

    @classmethod
    def from_properties(cls, x_pos:float, y_pos:float, y_vel:float, pressed:int):
        return cls([x_pos, y_pos, y_vel, pressed])