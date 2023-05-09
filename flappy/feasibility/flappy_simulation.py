""" Interfaces for doing reachability and feasibility analysis of flappy bird
"""
import time
from copy import deepcopy
from typing import List, Tuple, Dict, Optional
from hybrid_models.hybrid_point import HybridPoint
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
       start_params (Dict): starting state of flappy the bird
       level (FlappyLevel): level to simulate on
       seed (int): seed to use for level generation
    """
    step_time: float
    level: FlappyLevel
    seed: Optional[int]

    def __init__(self, t_max: float, j_max: int, step_time: float, start_params: Dict, seed: Optional[int] = None):
        """set up everything required for a sim run.
        Args:
            t_max (float): see class attribute of the same name
            j_max (int): see class attribute of hte same name
            step_time (float): see class attribute of the same name
            seed (Optional[int]): see class attribute of the same name
        """
        self.model = BackwardsFlappyModel(
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
    
    def feasibility_set(self, start_state, goal_x_pos, points_per_stride) -> List[HybridResult]:
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
        # update model state
        self.model.start_state = start_state

        if self.model.start_state.x_pos <= goal_x_pos:
            print(f"... found a good solution!")
            return []
 
        # just going to try and return all the bounds checks
        upper_bound, lower_bound = self._get_input_sequence_bounds()
        if upper_bound is None or lower_bound is None:
            return []

        found_solutions: List[HybridResult] = []        
        gen = btn_1_bounded_sequence_generator(upper_bound, lower_bound, points_per_stride)
        for input_sequence in gen:
            self.model.input_sequence = input_sequence
            print(f"Model start state while finding points: {self.model.start_state}")
            solver = HyEQSolver(self.model)
            solution = solver.solve()
            if not solution:
                return []
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
            # FIXME this sucks, memorizing around a function call sucks
            #       there has got to be a better way to set up this recursion
            restore_state = self.model.start_state
            found_solutions += self.feasibility_set(last_solve_state, goal_x_pos, points_per_stride)
            self.model.start_state = restore_state

        return found_solutions

    def _plot_bounds_recursively(self, start_state, goal_x_pos, points_per_stride) -> List[HybridResult]:
        """ Utility function to plot just the bounds of a backwards flappy solution
        """
        # FIXME DELETE EVENTUALLY
        self.model.start_state = start_state

        if self.model.start_state.x_pos <= goal_x_pos:
            #print(f"... found a good solution!")
            return []

        upper_solutions, lower_solutions = self._plot_input_sequence_bounds()
        upper_bound = [solution for solution in upper_solutions if solution.successful == True]
        lower_bound = [solution for solution in lower_solutions if solution.successful == True]
        
        if not upper_bound or not lower_bound:
            return []

        # jankerific unpack operation        
        found_bounds:List[HybridResult] = [upper_bound[0], lower_bound[0]]
        upper_bound_input = upper_bound[0].input_sequence         
        lower_bound_input = lower_bound[0].input_sequence
        print(f"Create a sequence generator from {upper_bound_input.samples} --> {lower_bound_input.samples}")
        gen = btn_1_bounded_sequence_generator(upper_bound_input, lower_bound_input, points_per_stride) #type: ignore it'll be there
        for input_sequence in gen:
            self.model.input_sequence = input_sequence
            #print(f"Model start state while finding points: {self.model.start_state}")
            solver = HyEQSolver(self.model)
            solution = solver.solve()
            if not solution:
                return []
            
            last_solve_state = solution[-1].state
            restore_state = self.model.start_state
            found_bounds += self._plot_bounds_recursively(last_solve_state, goal_x_pos, points_per_stride)
            self.model.start_state = restore_state

        return found_bounds

    def _plot_input_sequence_bounds(self) -> Tuple[List[HybridResult], List[HybridResult]]:
        """ Hack to just check the bounds that we're calculating
        """
        # TODO DELETE EVENTUALLY
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
        return (upper_solutions, lower_solutions)


    def _find_reachability_bound_given_order(self, input_generator) -> List[HybridResult]:
        """ raw iterative method. There might be a away to speed this up but /shrug
        """
        solutions: List[HybridResult] = []
        done = False
        input_sequence = None
        # this algorithm only makes sense for models with an input sequence
        if not hasattr(self.model, 'input_sequence'):
            raise RuntimeError("Provided model does not have an input sequence")
    
        while not done:
            # get an input sequence if we haven't gotten one yet
            single_run_start = time.time()
            if not input_sequence:
                input_sequence = input_generator.send(
                    None
                )  # explicit about getting the first element from the generator
            self.model.input_sequence = input_sequence #type: ignore models that make it this far have input sequences
            #print(
            #    f"Simulating: {''.join([str(sample) for sample in self.model.input_sequence.samples])}" #type: ignore models that make it this far have input sequences
            #)
            solver = HyEQSolver(self.model)
            solution = solver.solve()
            if not solution:
                print("Got a completely blank solution from the solver")
                print("May mean an invalid start state?")
                # solution is the empty array. I think this means that we shouldn't
                # even try other input sequences?
                done = True
                # the solution is just a single failed point at the start state
                solutions.append(HybridResult(False, input_sequence, [HybridPoint(0.0, self.model.start_state, 0)]))
            elif solver.stop == True:
                # normal failed run path
                solutions.append(HybridResult(False, input_sequence, solution))
                try:
                    input_sequence = input_generator.send(None)
                except StopIteration:
                    # We're in a state where we can't actually keep going-- we're invalid, there's
                    # no input sequence that we can take to get out of this one
                    done = True
            elif solver.stop == False:
                # This is the upper bound
                solutions.append(HybridResult(True, input_sequence, solution))
                done = True
            #if not done:
            #    print(
            #        f"Time spent solving: {solve_stop_time - single_run_start:0.02f}s"
            #    )
        if solutions and solutions[-1].successful == True:
            pass
            #print("...Valid solution found!")
            #print(f"{solutions[-1].input_sequence.samples}")  # type:ignore
        return solutions


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
        lower_bound = [solution for solution in lower_solutions if solution.successful == True]
        # FIXME jankerific unpack
        if len(lower_bound) > 0:
            lower_bound = lower_bound[0]
        else:
            print("Unable to find a lower bound, returning an empty set")
            return None, None
 
        return upper_bound.input_sequence, lower_bound.input_sequence

