""" Flappy state! As a list serializable class
"""
from dataclasses import dataclass
from typing import List
from hybrid_models.list_serializable import ListSerializable


@dataclass
class FlappyState(ListSerializable):
    x_pos: float
    y_pos: float
    y_vel: float
    pressed: int

    def to_list(self) -> List:
        return [self.x_pos, self.y_pos, self.y_vel, self.pressed]
