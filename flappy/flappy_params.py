"""Model class for some flappy parameters
"""
from dataclasses import dataclass

@dataclass
class FlappyParams():
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