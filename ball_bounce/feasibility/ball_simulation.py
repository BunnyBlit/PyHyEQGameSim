""" Interface for doing a single shot run of a bouncing ball simulation
"""
from copy import deepcopy
from hybrid_models.hybrid_simulation import HybridSim
from ..ball_state import BallState
from ..ball_params import BallParams
from .ball_model import BackwardBallModel
from hybrid_models.hybrid_solver import HyEQSolver
from hybrid_models.hybrid_result import HybridResult
from pprint import pprint, pformat
#from viztracer import VizTracer

class FeasibilityBallSim(HybridSim[BackwardBallModel]):
    """Class to manage simulation runs, and an interface to Do The Thing. This is for backwards
        in-time-feasibility runs
    """

    def __init__(self, t_max: float, j_max:int):
        """set up everything required for a sim run.
        Args:
            t_max (float): see class attribute of the same name
            j_max (int): see class attribute of the same name
        """
        self.model = BackwardBallModel(
            BallState.from_properties(y_pos=-0.0091, y_vel=-1.5696),
            BallParams(gamma=9.81, restitution_coef=0.5),
            t_max,
            j_max
        )

    def single_run(self) -> HybridResult:
        """Perform a single run
        Returns:
            HybridResult: the result of this simulation
        """
        solver = HyEQSolver(self.model)
        solution = solver.solve()
        
        # ok, so our hybrid result is in the correct direction, but the times are gonna be
        # backwards, so we remap them.
        max_solve_time = max([point.time for point in solution])
        max_solve_jumps = max([point.jumps for point in solution])
        for idx, new_time, new_jumps in zip(
                [i for i in range(0, len(solution))],
                [abs(max_solve_time - point.time) for point in solution],
                [abs(max_solve_jumps - point.jumps) for point in solution]):
            solution[idx].time = new_time
            solution[idx].jumps = new_jumps

        return HybridResult(not solver.stop, None, solution)
