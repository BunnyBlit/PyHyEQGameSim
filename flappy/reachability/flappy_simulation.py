""" Interfaces for doing reachability and feasibility analysis of flappy bird
"""
import time
from copy import deepcopy
from typing import List, Tuple, Generator, Optional
from .flappy_model import ForwardFlappyModel
from ..flappy_state import FlappyState
from ..flappy_level import FlappyLevel
from ..flappy_params import FlappyParams
from input.input_generators import btn_1_ordered_sequence_generator, time_sequence
from input.input_signal import InputSignal
from hybrid_models.hybrid_solver import HyEQSolver
from hybrid_models.hybrid_result import HybridResult


class ReachabilityFlappySim:
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
        self.start_state = FlappyState.from_properties(x_pos=0.1, y_pos=2.0, y_vel=0.1, pressed=0)
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
        model = ForwardFlappyModel(
            start_state=deepcopy(self.start_state),
            system_params=self.system_params,
            t_max=self.t_max,
            j_max=self.j_max,
            level=self.level,
        )
        model.input_sequence = input_sequence
        solver = HyEQSolver(model)
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
        upper_solutions = self.find_reachability_bound_given_order(upper_input_gen)
        # upper_solutions = []
        # print("Done!")
        print("... starting on lower bound ...")
        # lower bound calc
        lower_input_gen = btn_1_ordered_sequence_generator(
            self.t_max, self.step_time, "asc"
        )
        lower_solutions = self.find_reachability_bound_given_order(lower_input_gen)
        print("Done!")
        stop = time.time()
        self.print_reachability_report(start, stop, upper_solutions, lower_solutions)
        return (upper_solutions, lower_solutions)

    def find_reachability_bound_given_order(
        self, input_generator: Generator[InputSignal, Optional[List], None]
    ) -> List[HybridResult]:
        """Function to find an upper or lower reachability bound, given an ordered input.
            Because flappy only has one button, we can order the input by how often that button is held down
            the "max" is the button being held down at all times (all 1s), the min is the button never being
            pressed (all 0s). We can count upward (or downward) in binary to get an input order!
            Going from all 0's up gives us our lower bound, and going from all 1s down gives us our upper bound
        Args:
            input_generator (Generator[InputSignal, Optional[List], None]): a generator that returns input in an
               increasing or decreasing order. The generator can also skip input, based on how far we've gotten.
        Returns:
            List[HybridResult]: all the runs it took to find the bound (or a massive list of failed runs if none could be found)
        """
        solutions: List[HybridResult] = []
        done = False
        input_sequence = None
        # deep copy here because the model can change the state, which can
        # bubble back to the init object
        model = ForwardFlappyModel(
            start_state=deepcopy(self.start_state),
            system_params=self.system_params,
            t_max=self.t_max,
            j_max=17,  # FIXME: do this smarter, it's just set to a big number so sim won't terminate early
            level=self.level,
        )
        while not done:
            # get an input sequence if we haven't gotten one yet
            single_run_start = time.time()
            if not input_sequence:
                input_sequence = input_generator.send(
                    None
                )  # explicit about getting the first element from the generator
            model.input_sequence = input_sequence
            print(
                f"Simulating: {''.join([str(sample) for sample in model.input_sequence.samples])}"
            )
            solver = HyEQSolver(model)
            solution = solver.solve()
            solve_stop_time = time.time()
            # FIXME: might want to add this explicitly to a solution,
            #       but a solution is valid if the solver didn't hard stop
            #       early
            if solver.stop == True:
                solutions.append(HybridResult(False, input_sequence, solution))
                # find the index of the last relevant input sample
                last_sim_time = solution[-1].time
                relevant_input = [
                    sample for time, sample in input_sequence if time <= last_sim_time
                ]
                try:
                    # time to skip some!
                    # if 1, 1, 1, 0, 0, 1, 0, 0 fails at the last 1, it doesn't matter what the right two
                    # values are: the sim never gets that far! We can skip sequences until the 1 is a new value,
                    # reducing how much we need to simulate
                    # NOTE: this concept probably generalizes via caching relevant input sequences + sim results
                    #       any new sequence that is the same as a partial sequence that we know fails, also fails,
                    #       and does not need to be simulated
                    input_sequence = input_generator.send(relevant_input)
                    skip_stop_time = time.time()
                except StopIteration:
                    # We're in a state where we can't actually keep going-- we're invalid, there's
                    # no input sequence that we can take to get out of this one
                    done = True
            elif solver.stop == False:
                # This is the upper bound
                solutions.append(HybridResult(True, input_sequence, solution))
                done = True
            skip_stop_time = time.time()
            if not done:
                print(
                    f"Time spent solving: {solve_stop_time - single_run_start:0.02f}s"
                )
                print(f"Time spent skipping: {skip_stop_time - solve_stop_time:0.02f}s")
        if solutions[-1].successful == True:
            print("...Valid solution found!")
            print(f"{solutions[-1].input_sequence.samples}")  # type:ignore
        return solutions

    def print_reachability_report(
        self, start: float, stop: float, upper_solutions: List, lower_solutions: List
    ) -> None:
        """Print out a block of info about how long the reachability calculations took"""
        print(f"Finished {self.t_max}s of game play in {stop - start:0.02f}s")
        print(f"Took {len(upper_solutions) + len(lower_solutions)} runs")
        print(
            f"... per run time: {(stop - start) / (len(upper_solutions) + len(lower_solutions)):0.02f}"
        )
        print(f"Level Seed: {self.level.seed}")
