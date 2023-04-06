""" Interfaces for doing reachability and feasibility analysis of flappy bird
"""
import time
from copy import deepcopy
from typing import List, Tuple, Generator, Optional
from .flappy_model import BackwardsFlappyModel
from ..flappy_state import FlappyState
from ..flappy_level import FlappyLevel
from ..flappy_params import FlappyParams
from input.input_generators import btn_1_ordered_sequence_generator, time_sequence
from input.input_signal import InputSignal
from hybrid_models.hybrid_solver import HyEQSolver
from hybrid_models.hybrid_result import HybridResult


class FeasibilityFlappySim:
    """Class to manage simulation runs, and an interface to Do The Thing.
    Attributes:
       t_max (float): max time for a sim run. If we get to t_max, we're successful
       j_max (int): max number of jumps for the sim to run. If we get to j_max, we're successful
       step_time (float): how far apart each sample of the input signal is
       start_state (FlappyState): starting state of flappy the bird
       level (FlappyLevel): level to simulate on
       seed (int): seed to use for level generation
    """

    t_max: float
    j_max: int
    step_time: float
    start_state: FlappyState
    system_params: FlappyParams
    level: FlappyLevel
    seed: Optional[int]

    def __init__(self, t_max: float, j_max: int, step_time: float, seed: Optional[int] = None):
        """set up everything required for a sim run.
        Args:
            t_max (float): see class attribute of the same name
            j_max (int): see class attribute of hte same name
            step_time (float): see class attribute of the same name
            seed (Optional[int]): see class attribute of the same name
        """
        self.start_state = FlappyState.from_properties(x_pos=1.77, y_pos=2.9459, y_vel=2.0, pressed=1)
        self.system_params = FlappyParams(
            pressed_x_vel=2.0, pressed_y_vel=2.0, gamma=9.81
        )
        self.t_max = t_max
        self.j_max = j_max
        self.step_time = step_time
        self.seed = seed
        self.level = FlappyLevel.simple_procedural_gen(seed)

    def single_run(self, direct_sequence: List[int]) -> HybridResult:
        """Perform a single run with the given parameters and the provided input samples
        Args:
            direct_sequence: the input samples to use for this run
        Returns:
            HybridResult: the result of this simulation
        """
        input_sequence = time_sequence(direct_sequence, self.step_time)
        # deep copy here because the model can change the state, which can
        # bubble back to the init parameters
        model = BackwardsFlappyModel(
            start_state=deepcopy(self.start_state),
            system_params=self.system_params,
            t_max=self.t_max,
            j_max=self.j_max,
            level=self.level,
        )
        print(input_sequence)
        model.input_sequence = input_sequence
        solver = HyEQSolver(model)
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

        # FIXME: might want to add this explicitly to the solver,
        #       but a solution is valid if the solver didn't hard stop
        #       early (solver.stop)
        return HybridResult(not solver.stop, input_sequence, solution)
