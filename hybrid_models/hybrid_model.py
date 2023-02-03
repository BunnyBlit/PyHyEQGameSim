""" Breathe sits over the hybrid_solver.HyEQSolver, defining the various functions and parameters
    HyEQ needs. A Breathe model needs to also come up with how we're passing input to the controlled
    hybrid system and a collision / interaction function.
"""
from abc import abstractmethod
from typing import Any, Tuple, Generic, Type, TypeVar
from .list_serializable import ListSerializable
from .hybrid_point import HybridPoint, T

G = TypeVar('G', bound=ListSerializable)

# Add another parameter for input sequences: models are parameterized by
#   T - the system's state information
#   G - global parameters to the system
#   I - how input comes into the system: one button? several buttons? joysticks?
class HybridModel(Generic[T, G]):
    """ Hybrid models need to define a bunch of things! There are 4 primary functions that
        a hybrid model must define:
            flow (time, state, jumps, *params) -> List
                this function tells us how to integrate for the continuous parts of space
                it returns dy/dt with respect to j and any other model parameters
            jump (time, state, jumps, *params) -> List
                this function tells us how to jump, when and how to set y to new values
                without integrating. We jump through space. Should return new values for y,
                given t, j and any other model parameters
            flow_check (time, state, jumps, *params) -> int
                this function tells us, given a t, y, j and model parameters, if we should be
                flowing or not. 0 for no flow, 1 for flow
            jump_check (time, state, jumps *params) -> int
                this function tells us, given a t, y, j and parameters, if we should be jumping
                or not
        
        A hybrid model may also define an input function (t, j) -> Any. This function may be called
        by flow, jump, flow_check or jump_check to see what the input at t, j is, which can change
        how they function
    Attributes:
        t_max (float): the maximum time we're going to simulate out to
        j_max (int): the maximum number of jumps we'll simulate out to
        start_state (T): the initial state of the system.
        state_factory (Type[T]): a constructor for T
        system_params (G): constant parameters of the system. If it changes, it
                            should be part of state, not parameters-- these should be constant           
    """
    t_max:float
    j_max:int
    start_state: T
    state_factory: Type[T]
    system_params: G

    @abstractmethod
    def flow(self, hybrid_state: HybridPoint[T]) -> T:
        """ Flow function! This should take in y and return dy/dt.
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            T: dy/dt! The derivative of y w.r.t t given t and j and params!
        """
        pass

    @abstractmethod
    def jump(self, hybrid_state: HybridPoint[T]) -> T:
        """ Jump function! This should return a new y after a jump, given t and j and params.
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            List: new y after the jump!
        """
        pass

    @abstractmethod
    def flow_check(self, hybrid_state: HybridPoint[T]) -> Tuple[int, bool]:
        """ Flow check! This should return 1 if we can flow, 0 otherwise
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            int: 1 for flowin', 0 for not flowin'
        """
        pass

    @abstractmethod
    def jump_check(self, hybrid_state: HybridPoint[T]) -> Tuple[int, bool]:
        """ Jump check! This should return 1 if we can jump, 0 otherwise
        Args:
            hybrid_state (HybridPoint[T]): the current solve state, along with
                                           the number of jumps and the current time
        Returns:
            int: 1 for jumpin', 0 for not jumpin'
        """
        pass

    def get_input(self, time:float, jumps:int) -> Any:
        """ Function to get input to use in the flow, jump, flow_check or jump_check
            functions. Unlike the above functions, you don't have to use this (some
            systems are not controlled), but should overwrite it to do anything useful
        Args:
            time (float): time of this particular input
            jumps (int): number of jumps that have happened so far
        Returns:
            Any: whatever you need it to return!
        """
        return None