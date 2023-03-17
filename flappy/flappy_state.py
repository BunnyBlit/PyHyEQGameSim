""" Flappy state! As a list serializable class
"""
from dataclasses import dataclass
from typing import List, Any, Union, Iterator
from collections.abc import Sequence

@dataclass(init=False)
class FlappyState(Sequence):
    """ State of Flappy the bird! Changes over solve time.
    Properties:
        x_pos (float): x position
        y_pos (float): y position
        y_vel (float): y velocity.
                       x_vel is constant and doesn't need to be part of state.
        pressed (int): if the button is pressed or not
    """
    # controlling types here via the properties
    # that sit over this list
    _data: List[Union[float, int]]

    def __init__(self, x_pos:float, y_pos:float, y_vel:float, pressed:int):
        self._data = [0.0, 0.0, 0.0, 0]
        self.x_pos=x_pos
        self.y_pos=y_pos
        self.y_vel=y_vel
        self.pressed=pressed

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
        # this is kinda where the wheels come off a bit
        # afaik, we can't hint mixed types in a list, and
        # can't update the individual values of a tuple
        return int(self._data[3])
    
    @pressed.setter
    def pressed(self, value:int):
        self._data[3] = value

    # and now implement the correct protocols
    def __getitem__(self, key:int):
        return self._data[key]

    def __len__(self):
        return len(self._data)   