"""Core class for solving a hybrid systems equation!
    FIXME: move notes from notebook to here
"""
from typing import Callable, List, Generic, Sequence
import scipy.integrate as integrate
from .hybrid_model import HybridModel
from .hybrid_point import HybridPoint, T
from copy import deepcopy

from pprint import pprint
class HyEQSolver(Generic[T]):
    """A python implementation of a hybrid equation solver!
    Attributes:
        model (HybridModel): The Hybrid Model of the game that we're trying to solve for
        rule (int): when there is ambiguity, if the solver should prioritize
                    jumps or flows
        cur_state (HybridPoint[T]): current state, as an instantaneous point
                                    in a running solution
        stop (bool): "stop right now" signal
        sol (List[HybridPoint[T]]): The list of hybrid points that are part of
                                    this hybrid solution
        max_step (float): the maximum step size of the underlying ODE solver
        rtol (float): the relative tolerance of the underlying ODE solver
        atol (float): the absolute tolerance of the underlying ODE solver
    """

    model: HybridModel
    rule: int
    cur_state: HybridPoint[T]
    stop: bool
    sol: List[HybridPoint[T]]
    max_step: float
    rtol: float
    atol: float

    def __init__(
        self,
        model: HybridModel,
        rule: int = 1,
        max_step: float = 0.01,
        rtol: float = 1e-6,
        atol: float = 1e-6,
    ):
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
        self.zero_events = self._create_event_functs(self.rule)

        # and initialize where solutions will live
        self.sol = []

    def _create_event_functs(self, rule) -> List[Callable]:
        """Zero crossing functions!
        Very not sure why these work, but they do maybe!
        """

        # get the first element (the int) part of the returns on our check
        # functions
        def inside_flow(t, state_values):
            model_state = self.model.state_factory(*state_values)
            hybrid_point_from_solver = HybridPoint(
                t,
                model_state,
                self.cur_state.jumps
                )
            return 2 * self.model.flow_check(hybrid_point_from_solver)[0]

        def inside_jump(t, state_values):
            model_state = self.model.state_factory(*state_values)
            hybrid_point_from_solver = HybridPoint(t, model_state, self.cur_state.jumps)
            return (
                2
                - self.model.flow_check(hybrid_point_from_solver)[0]
                - self.model.jump_check(hybrid_point_from_solver)[0]
            )

        def outside_flow(t, state_values):
            model_state = self.model.state_factory(*state_values)
            hybrid_point_from_solver = HybridPoint(t, model_state, self.cur_state.jumps)
            return 2 * (-self.model.flow_check(hybrid_point_from_solver)[0])

        functs = [inside_flow, inside_jump, outside_flow]
        if rule == 1:
            functs[0].terminal = True
            functs[0].direction = -1
            functs[1].terminal = True
            functs[1].direction = -1
            functs[2].terminal = True
            functs[2].direction = 1
        elif rule == 2:
            functs[0].terminal = True
            functs[0].direction = -1
            functs[1].terminal = False
            functs[1].direction = -1
            functs[2].terminal = True
            functs[2].direction = 1

        return functs

    def _flow_wrapper(self, t: float, x: Sequence) -> List:
        """This is what the underlying solver is gonna call to get dy/dt
           values. As we're using somewhat more complicated types, I
           wrap that call so we can go to and from our types
        """
        # FIXME: I think I'm eating a lot of object creation time when I don't
        #       need to be here. Flowing isn't, really, state, and models
        #       currently return it as one.
        hybrid_point_from_solver = HybridPoint(
            t, self.model.state_factory(*x), self.cur_state.jumps
        )
        result = self.model.flow(hybrid_point_from_solver)
        return result

    def jump(self) -> None:
        """Perform a model jump! Call jump with the appropriate arguments"""
        self.cur_state.state = self.model.jump(self.cur_state)
        self.cur_state.jumps += 1

    def solve(self) -> List[HybridPoint[T]]:
        # if we're in a start state that jumps and we're prioritizing jumps,
        # jump immediately
        if self.rule == 1:
            # FIXME: This can probably get cleaned up-- something like
            # a jmp_priority function or something.
            while self.cur_state.jumps < self.model.j_max:
                should_jump, self.stop = self.model.jump_check(self.cur_state)
                if should_jump == 1 and not self.stop:
                    self.jump()
                else:
                    break

        if self.stop:
            return self.sol

        while (
            self.cur_state.jumps < self.model.j_max
            and self.cur_state.time < self.model.t_max
        ):
            should_flow, self.stop = self.model.flow_check(self.cur_state)
            if should_flow == 1 and not self.stop:
                ode_sol = integrate.solve_ivp(
                    self._flow_wrapper,
                    (self.cur_state.time, self.model.t_max),
                    self.cur_state.state,
                    events=self.zero_events,
                    max_step=self.max_step,
                    atol=self.atol,
                    rtol=self.rtol,
                )

                # a little error handling, as a treat
                # also fast fail, something's weird and up
                if ode_sol.status == -1:
                    return self.sol
                for time, state_values in zip(ode_sol.t, ode_sol.y.T):
                    new_state = self.model.state_factory(*state_values)
                    new_point = HybridPoint(time, new_state, self.cur_state.jumps)
                    self.sol.append(new_point)

                # FIXME: there's probably a smart way to do this,
                #        but the current state may get mutated by jumps
                #        and this lets us hold onto both sides of the instantaneous change
                #        (self.sol[-1] is pre change and self.cur_state will become post change)
                self.cur_state = deepcopy(self.sol[-1])

            # check stop signal
            if self.stop:
                return self.sol

            # and now check jumps
            should_jump, self.stop = self.model.jump_check(self.cur_state)
            if should_jump == 1 and not self.stop:
                # do as many jumps as possible
                if self.rule == 1:
                    while self.cur_state.jumps < self.model.j_max:
                        self.jump()
                        should_jump, self.stop = self.model.jump_check(self.cur_state)
                        if should_jump == 1 and not self.stop:
                            continue
                        else:
                            break
                # only do 1 jump
                else:
                    self.jump()
            else:
                break

        return self.sol
