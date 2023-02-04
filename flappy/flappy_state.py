""" Flappy state! As a list serializable class
"""
from dataclasses import dataclass
from typing import List
from hybrid_models.list_serializable import ListSerializable


@dataclass
class FlappyState(ListSerializable):
    """ State of Flappy the bird! Changes over solve time.
    Args:
        x_pos (float): x position
        y_pos (float): y position
        y_vel (float): y velocity.
                       x_vel is constant and doesn't need to be part of state.
        pressed (int): if the button is pressed or not
    """
    x_pos: float
    y_pos: float
    y_vel: float
    pressed: int

    def to_list(self) -> List:
        """Convert state to a list for use with the solver.
           The order is [x_pos, y_pos, y_vel, pressed]
        """
        return [self.x_pos, self.y_pos, self.y_vel, self.pressed]
