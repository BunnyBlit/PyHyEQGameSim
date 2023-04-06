""" Hybrid model for flappy bird
"""
from typing import List, Tuple
from hybrid_models.hybrid_model import HybridModel
from hybrid_models.hybrid_point import HybridPoint
from input.input_signal import InputSignal
from ..flappy_state import FlappyState
from ..flappy_params import FlappyParams
from ..flappy_level import FlappyLevel


class ForwardFlappyModel(HybridModel[FlappyState, FlappyParams]):
    """It's a hybrid model for flappy bird!
       Implements the 4 big functions for hybrid models,
       as well as a way to get input. For flappy, input is a single button 0 (off) or 1 (on)
    Attributes:
        start_state (FlappyState): Flappy's start state
        system_params (FlappyParams): constants for simulating flappy
        level (FlappyLevel): Level to simulate for Flappy
        t_max (float): max time to simulate out to
        j_max (int): max number of jumps to simulate out to
        input_sequence (InputSignal): the input sequence to use for simulation
    """

    start_state: FlappyState
    system_params: FlappyParams
    level: FlappyLevel
    t_max: float
    j_max: int
    input_sequence: InputSignal
    def __init__(
        self,
        start_state: FlappyState,
        system_params: FlappyParams,
        level: FlappyLevel,
        t_max: float = 2.0,
        j_max: int = 8,
        input_sequence: InputSignal = InputSignal([], []),
    ):
        """Constructor"""
        super().__init__()
        self.input_sequence: InputSignal = input_sequence
        self.j_max = j_max
        self.t_max = t_max
        self.start_state = start_state
        self.system_params = system_params
        self.state_factory = FlappyState
        self.level = level

    def get_input(self, time: float, jumps: int) -> int:
        """ Sample the input signal for the value of input at the provided time, jumps
           for flappy bird.
        Args:
           time (float): current sim time
           jumps (int): current number of sim jumps
        Returns:
           int: value if the input signal is pressed or not
        """
        if not self.input_sequence:
            raise RuntimeError("Need to set an input sequence before getting input!")
        
        # input_sequence is sorted according to time
        # FIXME: which means there is a better way to do this
        best_value = None
        best_time = float("inf")
        # we want to find the closest sample to (time) without going over
        # i.e.: never use a future sample to figure out the current value
        for sample_time, sample_value in self.input_sequence:
            temporal_distance = time - sample_time
            if temporal_distance < 0:
                continue
            if temporal_distance < best_time:
                best_time = temporal_distance
                best_value = sample_value

        if best_value is None:
            raise Exception("Unable to find a good sample!")

        return int(best_value)

    def check_collisions(self, state: FlappyState) -> bool:
        """ Check to see if we're colliding with anything. For flappy, this should
            stop the sim (we died).
        Args:
            state (FlappyState): current state to check for collisions
        Returns:
            bool: True = collision, False = no collision
        """
        # before we get into obstacles, do some simple "bird must be between these these two
        # heights" checks
        if state.y_pos <= self.level.lower_bound:
            return True
        if state.y_pos >= self.level.upper_bound:
            return True

        # very simple collision detection
        for obstacle in self.level.obstacles:
            bottom_left_coord, top_right_coord = obstacle
            if (
                state.x_pos >= bottom_left_coord[0]
                and state.x_pos <= top_right_coord[0]
                and state.y_pos >= bottom_left_coord[1]
                and state.y_pos <= top_right_coord[1]
            ):
                return True

        return False

    def flow(self, hybrid_state: HybridPoint[FlappyState]) -> FlappyState:
        """Flow function! This should take in y and return dy/dt.
        Args:
            hybrid_state: (HybridPoint[FlappyState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            FlappyState: d[state]/d[time]! The derivative of state w.r.t time given time, number of jumps and system params!
        """
        state = hybrid_state.state
        # NOTE: we currently overwrite the state and return the same state back
        #       this works, even though it doesn't make any goddamn sense.
        if state.pressed == 0:  # falling
            state.x_pos = self.system_params.pressed_x_vel
            state.y_pos = state.y_vel
            state.y_vel = -self.system_params.gamma
            state.pressed = 0
            return state
        else:  # flapping (pressed == 1)
            state.x_pos = self.system_params.pressed_x_vel
            state.y_pos = self.system_params.pressed_y_vel
            state.y_vel = 0
            state.pressed = 0
            return state

    def jump(self, hybrid_state: HybridPoint[FlappyState]) -> FlappyState:
        """Jump function! This should return a new state after a jump,
           given time and number of jumps and params.
        Args:
            hybrid_state: (HybridPoint[FlappyState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            FlappyState: new state after the jump!
        """
        state = hybrid_state.state
        time = hybrid_state.time
        jumps = hybrid_state.jumps
        # sample input signal
        new_pressed = self.get_input(time, jumps)
        state.pressed = new_pressed
        # jump according to the new input signal
        if new_pressed == 1:
            state.y_vel = self.system_params.pressed_y_vel

        return state

    def flow_check(self, hybrid_state: HybridPoint[FlappyState]) -> Tuple[int, bool]:
        """Flow check! This function checks if we can flow.
        Args:
            hybrid_state: (HybridPoint[FlappyState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            tuple with two elements:
                int: 1 for flowin', 0 for not flowin'
                bool: stop signal, if this is true we need to completely stop the model
                      false means keep going
        """
        state = hybrid_state.state
        time = hybrid_state.time
        jumps = hybrid_state.jumps
        colliding = self.check_collisions(state)
        if colliding:
            return (0, True)

        new_pressed = self.get_input(time, jumps)
        if new_pressed != state.pressed:
            return (0, False)

        return (1, False)

    def jump_check(self, hybrid_state: HybridPoint[FlappyState]) -> Tuple[int, bool]:
        """Jump check! This should return 1 if we can jump, 0 otherwise
        Args:
            hybrid_state: (HybridPoint[FlappyState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            tuple of two elements:
                int: 1 for jumpin', 0 for not jumpin'
                bool: stop signal, if this is true we need to completely stop the model
                      false means keep going
        """
        state = hybrid_state.state
        time = hybrid_state.time
        jumps = hybrid_state.jumps
        colliding = self.check_collisions(state)
        if colliding:
            return (0, True)

        new_pressed = self.get_input(time, jumps)
        if new_pressed != state.pressed:
            return (1, False)
        return (0, False)
