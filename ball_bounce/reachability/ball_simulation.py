""" Interface for doing a single shot run of a bouncing ball simulation
"""
from copy import deepcopy
from typing import Dict
from hybrid_models.hybrid_simulation import HybridSim
from ..ball_state import BallState
from ..ball_params import BallParams
from .ball_model import ForwardBallModel
from hybrid_models.hybrid_solver import HyEQSolver
from hybrid_models.hybrid_result import HybridResult
from pprint import pprint, pformat
#from viztracer import VizTracer

class ReachabilityBallSim(HybridSim[ForwardBallModel]):
    """Class to manage simulation runs, and an interface to Do The Thing.
    """

    def __init__(self, t_max: float, j_max:int, start_state:Dict):
        """set up everything required for a sim run.
        Args:
            t_max (float): see class attribute of the same name
            j_max (int): see class attribute of the same name
        """
        self.model = ForwardBallModel(
            BallState.from_properties(**start_state),
            BallParams(gamma=9.81, restitution_coef=0.5),
            t_max,
            j_max
        ) 
