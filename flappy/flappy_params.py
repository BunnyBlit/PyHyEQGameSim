"""Model class for some flappy parameters
"""
from dataclasses import dataclass
from typing import List
from hybrid_models.list_serializable import ListSerializable


@dataclass
class FlappyParams(ListSerializable):
    """Constant parameters for flappy. These values never change throughout
       a simulation run.
    Attributes:
        pressed_x_vel (float): flappy's horizontal velocity.
        # FIXME: This is actually has nothing to do with the button being pressed, should just be x_vel
        pressed_y_vel (float): flappy's upward velocity when the button is pressed
        gamma (float): acceleration due to gravity
    """
    pressed_x_vel: float
    pressed_y_vel: float
    gamma: float

    def to_list(self) -> List:
        """Convert the params to a list, the order is
           [pressed_x_vel, pressed_y_vel, gamma]
        """
        return [self.pressed_x_vel, self.pressed_y_vel, self.gamma]
