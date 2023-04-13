""" Interfaces for doing reachability and feasibility analysis of flappy bird
"""
import time
from copy import deepcopy
from typing import List, Tuple, Dict, Optional
from .flappy_model import ForwardFlappyModel
from ..flappy_state import FlappyState
from ..flappy_level import FlappyLevel
from ..flappy_params import FlappyParams
from input.input_generators import btn_1_ordered_sequence_generator, time_sequence
from input.input_signal import InputSignal
from hybrid_models.hybrid_solver import HyEQSolver
from hybrid_models.hybrid_result import HybridResult
from hybrid_models.hybrid_simulation import HybridSim

class ReachabilityFlappySim(HybridSim[ForwardFlappyModel]):
    """Class to manage simulation runs, and an interface to Do The Thing.
    Attributes:
       t_max (float): max time for a sim run. If we get to t_max, we're successful
       j_max (int): max number of jumps for the sim to run. If we get to j_max, we're successful
       step_time (float): how far apart each sample of the input signal is
       start_state (FlappyState): starting state of flappy the bird
       level (FlappyLevel): level to simulate on
       seed (int): seed to use for level generation
    """
    step_time: float
    level: FlappyLevel

    def __init__(self, t_max: float, j_max: int, step_time: float, start_params:Dict, seed: Optional[int] = None):
        """set up everything required for a sim run.
        Args:
            t_max (float): see class attribute of the same name
            j_max (int): see class attribute of hte same name
            step_time (float): see class attribute of the same name
            seed (Optional[int]): see class attribute of the same name
        """
        self.model = ForwardFlappyModel(
            deepcopy(FlappyState.from_properties(**start_params)),
            FlappyParams(pressed_x_vel=2.0, pressed_y_vel=2.0, gamma=9.81),
            FlappyLevel.simple_procedural_gen(seed),
            t_max,
            j_max
        )
        self.t_max = t_max
        self.j_max = j_max
        self.step_time = step_time
        self.seed = seed

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
        self.model.input_sequence = input_sequence
        solver = HyEQSolver(self.model)
        solution = solver.solve()

        # FIXME: might want to add this explicitly to the solver,
        #       but a solution is valid if the solver didn't hard stop
        #       early (solver.stop)
        return HybridResult(not solver.stop, input_sequence, solution)

    def reachability_simulation(self) -> Tuple[List[HybridResult], List[HybridResult]]:
        """Do a reachability analysis of Flappy
        Returns:
            Tuple[
                List[HybridResult]: all the runs to find the upper reachability bound
                List[HybridResult]: all the runs to find the lower reachability bound
            ]
        """
        start = time.time()
        # upper bound calc
        upper_input_gen = btn_1_ordered_sequence_generator(
            self.t_max, self.step_time, "dsc"
        )
        upper_solutions = self._find_reachability_bound_given_order(upper_input_gen)
        # lower bound calc
        lower_input_gen = btn_1_ordered_sequence_generator(
            self.t_max, self.step_time, "asc"
        )
        lower_solutions = self._find_reachability_bound_given_order(lower_input_gen)
        print("Done!")
        stop = time.time()
        self._print_reachability_report(start, stop, upper_solutions, lower_solutions)
        return (upper_solutions, lower_solutions)

    
