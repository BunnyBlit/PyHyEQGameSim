"""A bouncing ball state! As a list serializable class
"""
from dataclasses import dataclass
from typing import List
from hybrid_models.list_serializable import ListSerializable

@dataclass
class BallState(ListSerializable):
    """State of a bouncing ball! We only care about one dimension,
        we're not worried about left/right position for a demo
    Args:
        y_pos (float): y position
        y_vel (float): y velocity
    """
    y_pos: float
    y_vel: float

    def to_list(self) -> List:
        """Convert state to a list for use with the solver.
           The order is [y_pos, y_vel, y_accel]
        """
        return [self.y_pos, self.y_vel]
