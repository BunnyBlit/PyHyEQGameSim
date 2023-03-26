""" Hybrid model for a bouncing ball
"""
from typing import List, Tuple
from hybrid_models.hybrid_model import HybridModel
from hybrid_models.hybrid_point import HybridPoint
from input.input_signal import InputSignal
from ..ball_state import BallState
from ..ball_params import BallParams


class BackwardBallModel(HybridModel[BallState, BallParams]):
    """It's a hybrid model for a bouncing ball backward-in-time!
       Implements the 4 big functions for hybrid models
       No input in this model. Ball's gonna bounce
    Attributes:
        start_state (BallState): The ball's start state
        system_params (BallParams): constants for simulating a bouncing ball
        t_max (float): max time to simulate out to
        j_max (int): max number of jumps to simulate out to
    """

    start_state: BallState
    system_params: BallParams
    t_max: float
    j_max: int
    input_sequence: InputSignal
    def __init__(
        self,
        start_state: BallState,
        system_params: BallParams,
        t_max: float = 2.0,
        j_max: int = 8,
    ):
        """Constructor"""
        super().__init__()
        self.j_max = j_max
        self.t_max = t_max
        self.start_state = start_state
        self.system_params = system_params
        self.state_factory = BallState

    def flow(self, hybrid_state: HybridPoint[BallState]) -> BallState:
        """Flow function! This should take in y and return dy/dt, for going backwards in time
        Args:
            hybrid_state: (HybridPoint[BallState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            BallState: d[state]/d[time]! The derivative of state w.r.t time given time, number of jumps and system params!
        """
        state = hybrid_state.state
        state.y_pos = state.y_vel
        state.y_vel = -self.system_params.gamma
        return state

    def jump(self, hybrid_state: HybridPoint[BallState]) -> BallState:
        """Jump function! This should return a new state before a jump (going backwards in time),
           given time and number of jumps and params.
        Args:
            hybrid_state: (HybridPoint[BallState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            FlappyState: new state after the jump!
        """
        state = hybrid_state.state
        print(f"Before: {state}")
        state.y_vel = state.y_vel / -self.system_params.restitution_coef
        print(f"After: {state}")
        return state

    def flow_check(self, hybrid_state: HybridPoint[BallState]) -> Tuple[int, bool]:
        """Flow check! This function checks if we can flow.
        Args:
            hybrid_state: (HybridPoint[BallState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            tuple with two elements:
                int: 1 for flowin', 0 for not flowin'
                bool: stop signal, if this is true we need to completely stop the model
                      false means keep going
        """
        return (1, False)

    def jump_check(self, hybrid_state: HybridPoint[BallState]) -> Tuple[int, bool]:
        """Jump check! This should return 1 if we can jump, 0 otherwise
        Args:
            hybrid_state: (HybridPoint[BallState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            tuple of two elements:
                int: 1 for jumpin', 0 for not jumpin'
                bool: stop signal, if this is true we need to completely stop the model
                      false means keep going
        """
        state = hybrid_state.state
        if state.y_pos <= 0 and state.y_vel < 0:
            print(f"TRIGGERED A JUMP:\t{state}")
            return (1, False)
        else:
            return (0, False)