""" Interface for doing a single shot run of a bouncing ball simulation
"""
from copy import deepcopy
from .ball_state import BallState
from .ball_params import BallParams
from .ball_model import BallModel
from hybrid_models.hybrid_solver import HyEQSolver
from hybrid_models.hybrid_result import HybridResult
from pprint import pprint, pformat

class BallSim:
    """Class to manage simulation runs, and an interface to Do The Thing.
    Attributes:
       t_max (float): max time for a sim run. If we get to t_max, we're successful
       j_max (int): max number of jumps for a sim run. If we get to j_max, we're successful
       step_time (float): how far apart each sample of the input signal is
       start_state (BallState): starting state of the bouncing ball
       system_params (BallParams): the constants for running a bouncing ball sim
    """
    t_max: float
    j_max: int
    step_time: float
    start_state: BallState
    system_params: BallParams

    def __init__(self, t_max: float, j_max:int):
        """set up everything required for a sim run.
        Args:
            t_max (float): see class attribute of the same name
            j_max (int): see class attribute of the same name
            step_time (float): see class attribute of the same name
            seed (Optional[int]): see class attribute of the same name
        """
        self.start_state = BallState(y_pos=2.0, y_vel=0.0)
        self.system_params = BallParams(
            gamma=9.81,
            restitution_coef=0.5
        )
        self.t_max = t_max
        self.j_max = j_max

    def single_run(self) -> HybridResult:
        """Perform a single run
        Returns:
            HybridResult: the result of this simulation
        """
        # deep copy here because the model can change the state, which can
        # bubble back to the init parameters
        model = BallModel(
            start_state=deepcopy(self.start_state),
            system_params=self.system_params,
            t_max=self.t_max,
            j_max=self.j_max,
        )
        solver = HyEQSolver(model)
        solution = solver.solve()
        # FIXME: might want to add this explicitly to the solver,
        #       but a solution is valid if the solver didn't hard stop
        #       early (solver.stop)
        return HybridResult(not solver.stop, None, solution)
