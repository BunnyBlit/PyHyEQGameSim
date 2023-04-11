""" Interfaces for doing reachability and feasibility analysis of flappy bird
"""
import time
from copy import deepcopy
from typing import List, Tuple, Generator, Optional
from hybrid_models.hybrid_simulation import HybridSim
from .flappy_model import BackwardsFlappyModel
from ..flappy_state import FlappyState
from ..flappy_level import FlappyLevel
from ..flappy_params import FlappyParams
from input.input_generators import btn_1_ordered_sequence_generator, btn_1_bounded_sequence_generator, time_sequence
from input.input_signal import InputSignal
from hybrid_models.hybrid_solver import HyEQSolver
from hybrid_models.hybrid_result import HybridResult


class FeasibilityFlappySim(HybridSim[BackwardsFlappyModel]):
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
    seed: Optional[int]

    def __init__(self, t_max: float, j_max: int, step_time: float, seed: Optional[int] = None):
        """set up everything required for a sim run.
        Args:
            t_max (float): see class attribute of the same name
            j_max (int): see class attribute of hte same name
            step_time (float): see class attribute of the same name
            seed (Optional[int]): see class attribute of the same name
        """
        self.model = BackwardsFlappyModel(
            deepcopy(FlappyState.from_properties(x_pos=1.7032, y_pos=2.8791, y_vel=2, pressed=1)),
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
        print(input_sequence)
        self.model.input_sequence = input_sequence
        solver = HyEQSolver(self.model)
        solution = solver.solve()

        # ok, so our hybrid result is in the correct direction, but the times are gonna be
        # backwards, so we remap them.
        max_solve_time = solution[-1].time
        max_solve_jumps = solution[-1].jumps
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
    
    def feasibility_set(self, goal_x_pos, points_per_stride) -> List[HybridResult]:
        """ Do a feasibility analysis of Flappy
        TODO: this function is written as _total_ side effect while doing the recursion
              that's bad! We prefer pure functions!
        Args:
            goal_x_pos (float): the x position we want to eventually get to
            points_per_stride (int): number of valid solutions to use per backwards stride
                                     -1 for all of them
        Returns:
            List: a list of hybrid results for the number of points we want
                  to simulate with
        """
        if self.model.start_state.x_pos <= goal_x_pos:
            return []

        upper_bound, lower_bound = self._get_input_sequence_bounds()
        print(f"Upper Bound:")
        print(upper_bound)
        print(f"Lower Bound:")
        print(lower_bound)

        if upper_bound is None or lower_bound is None:
            return []
        
        found_solutions: List[HybridResult] = []
        gen = btn_1_bounded_sequence_generator(upper_bound, lower_bound, points_per_stride)
        for input_sequence in gen:
            self.model.input_sequence = input_sequence
            solver = HyEQSolver(self.model)
            solution = solver.solve()
            # NOTE: time on these solutions is fucky-wucky
            # .     basically: because we're going back in steps
            #       we have no idea where the first time point is
            #       but we always solve "forward" in time
            # ok, so our hybrid result is in the correct direction, but the times are gonna be
            # backwards, so we remap them.
            last_solve_state = solution[-1].state
            max_solve_time = solution[-1].time
            max_solve_jumps = solution[-1].jumps
            for idx, new_time, new_jumps in zip(
                [i for i in range(0, len(solution))],
                [abs(max_solve_time - point.time) for point in solution],
                [abs(max_solve_jumps - point.jumps) for point in solution]):
                    solution[idx].time = new_time
                    solution[idx].jumps = new_jumps
            found_solutions.append(HybridResult(not solver.stop, input_sequence, solution))
            # FIXME this sucks. this being entirely side effect is bad
            self.model.start_state = last_solve_state
            found_solutions += self.feasibility_set(goal_x_pos, points_per_stride)


        return found_solutions
    
    def _get_input_sequence_bounds(self) -> Tuple[Optional[InputSignal], Optional[InputSignal]]:
        """ Get upper and lower bounds on an input sequence for flappers
        """
        upper_input_gen = btn_1_ordered_sequence_generator(
            self.t_max, self.step_time, "dsc"
        )
        upper_solutions = self._find_reachability_bound_given_order(upper_input_gen)
        upper_bound = [solution for solution in upper_solutions if solution.successful == True]
        # FIXME jankerific unpack
        if len(upper_bound) > 0:
            upper_bound = upper_bound[0]
        else:
            print("Unable to find an upper bound, returning an empty set")
            return None, None

        lower_input_gen = btn_1_ordered_sequence_generator(
            self.t_max, self.step_time, "asc"
        )
        lower_solutions = self._find_reachability_bound_given_order(lower_input_gen)
        lower_bound = [solution for solution in upper_solutions if solution.successful == True]
        # FIXME jankerific unpack
        if len(lower_bound) > 0:
            lower_bound = lower_bound[0]
        else:
            print("Unable to find a lower bound, returning an empty set")
            return None, None
        
        return upper_bound.input_sequence, lower_bound.input_sequence

