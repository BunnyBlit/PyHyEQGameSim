"""Model class for some flappy parameters
"""
from dataclasses import dataclass
from typing import List
from hybrid_models.list_serializable import ListSerializable

@dataclass
class FlappyParams(ListSerializable):
    pressed_x_vel: float
    pressed_y_vel: float
    gamma: float

    def to_list(self) -> List:
        """ Convert the params to a list
        """
        return [self.pressed_x_vel, self.pressed_y_vel, self.gamma]
