"""Core class for solving a hybrid systems equation!
    FIXME: move notes from notebook to here
"""
from typing import Callable, List, Generic, Sequence, Any
import scipy.integrate as integrate

from .hybrid_model import HybridModel
from .hybrid_point import HybridPoint, T

from pprint import pformat, pprint


class HyEQSolver(Generic[T]):
    """ A python implementation of a hybrid equation solver! Based on a matlab implementation
        that I have somewhere!
    Attributes:
        flow_map (Callable): a function that returns the derivatives of the current state. Used as part
                             of solving a simple ODE problem, and how we simulate the consequences of hitting
                             buttons / the continuous part of game state
        jump_map (Callable): a function that returns a new state given an old state. Used for modeling the instantaneous
                             part of a how a game changes (responses to button presses, dying, etc)
        flow_set (Callable): function that returns if we should be flowing or not (solving the continuous part of space)
                              Returns a tuple: int for flowing or not (1 for flow, 0 for no flow) and a "stop right now" boolean
        jump_set (Callable): function that returns if we should jump right now or not.
                              Returns a tuple: int for jumping (1 to jump, 0 to not jump) and a "stop right now" boolean
        rule (int): when there is ambiguity, if the solver should prioritize jumps or flows
        cur_state (HybridPoint[T]): current state, as an instantaneous point in a running solution
        y (T): the current state
        t (float): the current time
        j (int): the current number of jumps we've taken so far
        stop (bool): "stop right now" signal
        sol (List[HybridPoint[T]]): The list of hybrid points that are part of this hybrid solution
    """
    model: HybridModel
    rule: int
    cur_state: HybridPoint[T]
    stop: bool
    sol: List[HybridPoint[T]]

    def __init__(self, model: HybridModel, rule:int=1, max_step:float=0.01, rtol:float=1e-6, atol:float=1e-6):
        """ There's a lot of stuff up there, see the notes before this section.
        """
        # Model to solve over
        self.model = model
        
        # Lots of solver parameters
        self.rule = rule
        self.max_step = max_step
        self.rtol = rtol
        self.atol = atol
        
        # solver state
        self.cur_state = HybridPoint(0.0, self.model.start_state, 0)
        self.stop = False

        # solver event functions
        self.zeroevents = self._create_event_functs(self.rule)

        # and initialize where solutions will live
        self.sol = [] 

    def _create_event_functs(self, rule) -> List[Callable]:
        """ Zero crossing functions!
            Very not sure why these work, but they do maybe!
        """
        # get the first element (the int) part of the returns on our check functions
        def inside_flow(t, state_values):
            model_state = self.model.state_factory(*state_values)
            hybrid_point_from_solver = HybridPoint(t, model_state, self.cur_state.jumps)
            return 2 * self.model.flow_check(hybrid_point_from_solver)[0]
            
        def inside_jump(t, state_values):
            model_state = self.model.state_factory(*state_values)
            hybrid_point_from_solver = HybridPoint(t, model_state, self.cur_state.jumps)
            return 2 - self.model.flow_check(hybrid_point_from_solver)[0] - self.model.jump_check(hybrid_point_from_solver)[0]
        
        def outside_flow(t, state_values):
            model_state = self.model.state_factory(*state_values)
            hybrid_point_from_solver = HybridPoint(t, model_state, self.cur_state.jumps)
            return 2 * (-self.model.flow_check(hybrid_point_from_solver)[0])

        functs = [inside_flow,
                  inside_jump,
                  outside_flow]
        if rule == 1:
            functs[0].terminal = 1
            functs[0].direction = -1
            functs[1].terminal = 1
            functs[1].direction = -1
            functs[2].terminal = 1
            functs[2].direction = 1
        elif rule == 2:
            functs[0].terminal = 1
            functs[0].direction = -1
            functs[1].terminal = 0
            functs[1].direction = -1
            functs[2].terminal = 1
            functs[2].direction = 1 

        return functs
    
    def _flow_wrapper(self, t:float, x:Sequence) -> List:
        """ This is what the underlying solver is gonna call to get dy/dt values.
            As we're using somewhat more complicated types, we're wrap that call
            so we can to and from our types
        """
        hybrid_point_from_solver = HybridPoint(t, self.model.state_factory(*x), self.cur_state.jumps)
        result = self.model.flow(hybrid_point_from_solver)
        return result.to_list()

    def jump(self) -> None:
        """ Perform a model jump! Call jump with the appropriate arguments
        """
        self.cur_state.state = self.model.jump(self.cur_state)
        self.cur_state.jumps += 1
        self.sol.append(self.cur_state)

    def solve(self) -> List[HybridPoint[T]]:
        # if we're in a start state that jumps and we're prioritizing jumps,
        # jump immediately
        # this impl also lets us jump more than once at a time
        if self.rule == 1:
            # FIXME: This can probably get cleaned up a lot-- something like
            # a jmp_priority function or something.
            while self.cur_state.jumps < self.model.j_max:
                should_jump, self.stop = self.model.jump_check(self.cur_state)
                if should_jump == 1 and not self.stop:
                    self.jump()
                else:
                    break
        
        if self.stop:
            return self.sol
        
        while self.cur_state.jumps < self.model.j_max and self.cur_state.time < self.model.t_max:
            should_flow, self.stop = self.model.flow_check(self.cur_state)
            if should_flow == 1 and not self.stop:
                ode_sol = integrate.solve_ivp(self._flow_wrapper,
                                                (self.cur_state.time, self.model.t_max),
                                                self.cur_state.state.to_list(),
                                                events=self.zeroevents,
                                                max_step=self.max_step,
                                                atol=self.atol,
                                                rtol=self.rtol)

                # a little error handling, as a treat
                # also fast fail, something's weird and up
                if ode_sol.status == -1:
                    print(ode_sol.message)
                    if ode_sol.message == "Required step size is less than spacing between numbers.":
                        pass
                    else:
                        return self.sol
                for time, state_values in zip(ode_sol.t, ode_sol.y.T):
                    new_state = self.model.state_factory(*state_values)
                    new_point = HybridPoint(time, new_state, self.cur_state.jumps)
                    self.sol.append(new_point)

                self.cur_state = self.sol[-1]
            
            # check stop signal
            if self.stop:
                return self.sol 

            # and now check jumps
            should_jump, self.stop = self.model.jump_check(self.cur_state)
            if should_jump == 1 and not self.stop:
                # do as many jumps as possible
                if self.rule == 1:
                    while self.cur_state.jumps < self.model.j_max:
                        should_jump, self.stop = self.model.jump_check(self.cur_state)
                        if should_jump == 1 and not self.stop:
                            self.jump()
                        else:
                            break
                # only do 1 jump
                else:
                    self.jump()
            else:
                break 

        # wrap this up nicely
        return self.sol