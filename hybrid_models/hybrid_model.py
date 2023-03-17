"""The abstract class for a Hybrid Equation model. These sit over the solver,
   which uses them to simulate how a game will respond to certain input sequences. 
"""
from abc import abstractmethod
from typing import Any, Tuple, Generic, Type, TypeVar
from .hybrid_point import HybridPoint, T

G = TypeVar("G")

# Add another parameter for input sequences: models are parameterized by
#   T - the system's state information
#   G - global parameters to the system
class HybridModel(Generic[T, G]):
    """Hybrid models need to define a bunch of things! There are 4 primary functions that
        a hybrid model must define:
            flow (hybrid_state: HybridPoint[T]) -> T
                this function tells us how to integrate for the continuous parts of space
                it returns d[state]/dt with respect to jumps and any other model parameters
            jump (hybrid_state: HybridPoint[T]) -> T
                this function tells us how to jump, when and how to set state to new values
                without integrating, a jump through state space. Should return new values for state,
                given time, jumps and any other model parameters
            flow_check (hybrid_state: HybridPoint[T]) -> Tuple[int, bool]
                this function tells us, given a HybridPoint, if we should be
                flowing or not. 0 for no flow, 1 for flow. If bool is true, we should stop simulating
            jump_check (hybrid_state: HybridPoint[T]) -> Tuple[int, bool]
                this function tells us, given a HybridPoint, if we should be jumping
                or not, 0 for no jump, 1 for jump. The bool part of the result tuple
                is for fast failing: if bool is true, we should stop simulating

        A hybrid model may also define an input function (time, jumps) -> Any. This function may be called
        by flow, jump, flow_check or jump_check to see what the input at time, jumps is, which can change
        how they function
    Attributes:
        t_max (float): the maximum time we're going to simulate out to
        j_max (int): the maximum number of jumps we'll simulate out to
        start_state (T): the initial state of the system.
        state_factory (Type[T]): a constructor for T
        system_params (G): constant parameters of the system. If it changes, it
                            should be part of state, not parameters-- these should be constant
    """

    t_max: float
    j_max: int
    start_state: T
    state_factory: Type[T]
    system_params: G

    @abstractmethod
    def flow(self, hybrid_state: HybridPoint[T]) -> T:
        """Flow function! This should take in y and return dy/dt.
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            T: dy/dt! The derivative of y w.r.t t given t and j and params!
        """
        pass

    @abstractmethod
    def jump(self, hybrid_state: HybridPoint[T]) -> T:
        """Jump function! This should return a new y after a jump, given t and j and params.
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            List: new y after the jump!
        """
        pass

    @abstractmethod
    def flow_check(self, hybrid_state: HybridPoint[T]) -> Tuple[int, bool]:
        """Flow check! This should return 1 if we can flow, 0 otherwise
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            int: 1 for flowin', 0 for not flowin'
        """
        pass

    @abstractmethod
    def jump_check(self, hybrid_state: HybridPoint[T]) -> Tuple[int, bool]:
        """Jump check! This should return 1 if we can jump, 0 otherwise
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            int: 1 for jumpin', 0 for not jumpin'
        """
        pass

    def get_input(self, time: float, jumps: int) -> Any:
        """Function to get input to use in the flow, jump, flow_check or jump_check
            functions. Unlike the above functions, you don't have to use this (some
            systems are not controlled), but should overwrite it to do anything useful
        Args:
            time (float): time of this particular input
            jumps (int): number of jumps that have happened so far
        Returns:
            Any: whatever you need it to return!
        """
        return None
