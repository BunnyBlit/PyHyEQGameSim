""" Base class for implementing common hybrid simulation tasks
    Contains some common search functions (find bounds given ordered input)
"""

from copy import deepcopy
import time
from typing import Generator, Optional, List, Generic, TypeVar

from hybrid_models.hybrid_solver import HyEQSolver
from .hybrid_model import HybridModel, T, G
from .hybrid_result import HybridResult
from input.input_signal import InputSignal
L = TypeVar("L") # level type var
M = TypeVar("M", bound=HybridModel) # model type var

class HybridSim(Generic[M]):
    """Class to manage simulation runs as an interface to do useful work with
       a hybrid system
       It's expected that subclasses override a lot of the functionality here,
       when they need it
    Attributes:
        model: (HybridModel) hybrid model to use for simulation
        t_max (float): max time for a sim run. If we get to t_max, we're successful
        j_max (int): max number of jumps for the sim to run. If we get to j_max, we're successful
        step_time (float, optional): how far apart each sample of the input signal is
        level (FlappyLevel, optional): level to simulate on
        seed (int, optional): seed to use for level generation
    """
    model: M
    t_max: float
    j_max: int
    step_time: Optional[float]
    seed: Optional[int]

    def single_run(self):
        """Do a single, no input run of the model
        """
        solver = HyEQSolver(self.model)
        solution = solver.solve()

        # FIXME: might want to add this explicitly to the solver,
        #       but a solution is valid if the solver didn't hard stop
        #       early (solver.stop)
        return HybridResult(not solver.stop, None, solution)

    def _find_reachability_bound_given_order(
        self,
        input_generator: Generator[InputSignal, Optional[List], None]
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
        # this algorithm only makes sense for models with an input sequence
        if not hasattr(self.model, 'input_sequence'):
            raise RuntimeError("Provided model does not have an input sequence")
        # deep copy here because the model can change the state, which can
        # bubble back to the init object
        while not done:
            # get an input sequence if we haven't gotten one yet
            single_run_start = time.time()
            if not input_sequence:
                input_sequence = input_generator.send(
                    None
                )  # explicit about getting the first element from the generator
            self.model.input_sequence = input_sequence #type: ignore models that make it this far have input sequences
            print(
                f"Simulating: {''.join([str(sample) for sample in self.model.input_sequence.samples])}" #type: ignore models that make it this far have input sequences
            )
            print(
                f"Start State: {self.model.start_state}"
            )
            solver = HyEQSolver(self.model)
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

                print(solution)
                import pdb; pdb.set_trace()
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

    def _print_reachability_report(
        self, start: float, stop: float, upper_solutions: List, lower_solutions: List
    ) -> None:
        """Print out a block of info about how long the reachability calculations took"""
        print(f"Finished {self.t_max}s of game play in {stop - start:0.02f}s")
        print(f"Took {len(upper_solutions) + len(lower_solutions)} runs")
        print(
            f"... per run time: {(stop - start) / (len(upper_solutions) + len(lower_solutions)):0.02f}"
        )
        print(f"Level Seed: {self.seed}")