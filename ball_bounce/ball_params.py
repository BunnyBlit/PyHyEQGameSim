"""Model class for some bouncing ball parameters
"""
from dataclasses import dataclass

@dataclass
class BallParams():
    """Constant parameters for a bouncing ball. These values never
       change over the course of a simulation run.
    Attributes:
        gamma (float): acceleration due to gravity
        restitution_coef (float): energy lost in a bounce
    """
    gamma: float
    restitution_coef: float
