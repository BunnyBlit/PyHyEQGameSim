"""Model class for some bouncing ball parameters
"""
from dataclasses import dataclass
from typing import List
from hybrid_models.list_serializable import ListSerializable


@dataclass
class BallParams(ListSerializable):
    """Constant parameters for a bouncing ball. These values never
       change over the course of a simulation run.
    Attributes:
        gamma (float): acceleration due to gravity
        restitution_coef (float): energy lost in a bounce
    """
    gamma: float
    restitution_coef: float

    def to_list(self) -> List:
        """Convert the params to a list, the order is
           [gamma]
        """
        return [self.gamma, self.restitution_coef]
