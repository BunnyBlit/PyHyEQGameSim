""" Hybrid model for flappy bird
"""
from typing import List, Tuple, cast
from hybrid_models.hybrid_model import HybridModel
from hybrid_models.hybrid_point import HybridPoint
from input.input_signal import InputSignal
from ..flappy_state import FlappyState
from ..flappy_params import FlappyParams
from ..flappy_level import FlappyLevel
from pprint import pprint, pformat

class BackwardsFlappyModel(HybridModel[FlappyState, FlappyParams]):
    """It's a hybrid model for flappy bird that works backwards-in-time!
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

    def get_input(self, time: float, jumps: int) -> Tuple[float, int]:
        """ Sample the input signal for the value of input at the provided time, jumps
           for flappy bird.
        Args:
           time (float): current sim time
           jumps (int): current number of sim jumps
        Returns:
            Tuple of [time, button value]
        """
        if not self.input_sequence:
            raise RuntimeError("Need to set an input sequence before getting input!")

        max_sample_time = self.input_sequence.times[-1]
        flipped_sample_time = abs(time - max_sample_time) if time < max_sample_time else 0.0 # need to ceiling this signal
        print(f"Get Input Time: {flipped_sample_time:0.4f}")
        # input_sequence is sorted according to time
        # FIXME: which means there is a better way to do this
        best_sample_idx = -1
        best_time = float("inf")
        # we want to find the closest sample to (time) without going over
        # i.e.: never use a future sample to figure out the current value
        for idx, sequence_values in enumerate(self.input_sequence):
            sample_time, _ = sequence_values
            temporal_distance = flipped_sample_time - sample_time
            if temporal_distance < 0:
                continue
            if temporal_distance < best_time:
                best_time = temporal_distance
                best_sample_idx = idx

        if best_sample_idx == -1:
            raise Exception("Unable to find a good sample!")

        # TODO: I have given up. There's just no good way to override __getitem__
        #       so it works like it does for Python builtins
        return_value = cast(Tuple[float, int], self.input_sequence[best_sample_idx])
        return return_value[0], return_value[1]

    def reverse_y_vel_from_signal(self, time: float, near_sample_time:float, jumps: int) -> float:
        """ Reverse calculate what the y_vel at the end of a falling state without needing to
            forward simulate it.
        """
        if not self.input_sequence:
            raise RuntimeError("Need to set an input sequence before using it to calculate a final y_vel")
        
        max_sample_time = self.input_sequence.times[-1]
        flipped_time = abs(time - max_sample_time) if time < max_sample_time else 0.0 # need to ceiling this signal

        print(f"Calculating final y vel for reverse at time: {flipped_time:0.4f} ({time:0.4f})")
        nearest_sample_idx = [idx for idx, sample_value in enumerate(self.input_sequence) if cast(Tuple[float, float | int], sample_value)[0] == near_sample_time][0]
        falling_samples = []
        print(f"Using input sample idx: {nearest_sample_idx}")
        print("value:")
        print(self.input_sequence[nearest_sample_idx])
        # FIXME: I don't think I'm handling strides correctly
        for signal in self.input_sequence[:nearest_sample_idx][::-1]:
            # TODO: see above, I can't figure out a good __getitem__ pattern
            #       so we have this unholy, slow hack instead
            signal = cast(Tuple[float, float | int], signal)
            time, sample_value = signal
            if sample_value == 0:
                falling_samples.append(signal)
            else:
                break
    
        print(f"Falling samples:\n{pformat(falling_samples)}")
        fall_start_time = falling_samples[-1][0] # comes from a backwards in time list
        print(f"Fall start time: {fall_start_time}")
        # OK! We have all the info we need
        ending_y_vel = self.system_params.pressed_y_vel + (-self.system_params.gamma) * (flipped_time - fall_start_time)
        print(f"Calculated ending y vel: {ending_y_vel}")
        return ending_y_vel

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
        """Flow function! This should take in y and return dy/dt for working backwards-in-time.
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
            state.x_pos = -self.system_params.pressed_x_vel
            state.y_pos = -state.y_vel
            state.y_vel = self.system_params.gamma
            state.pressed = 0
        else:  # flapping (pressed == 1)
            state.x_pos = -self.system_params.pressed_x_vel
            state.y_pos = -self.system_params.pressed_y_vel
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
        sample_time, new_pressed = self.get_input(time, jumps)
        state.pressed = new_pressed
        # jump according to the new input signal
        if new_pressed == 1:
            state.y_vel = -self.system_params.pressed_y_vel
        else:
            # peek back at the input signal, figure out how long flappers has been falling for
            # and set the y vel accordingly
            state.y_vel = self.reverse_y_vel_from_signal(time, sample_time, jumps)

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

        _, new_pressed = self.get_input(time, jumps)
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

        _, new_pressed = self.get_input(time, jumps)
        print(f"{time:0.4f}\t{state.pressed} --> {_:0.04f}\t{new_pressed}")
        if new_pressed != state.pressed:
            print(f"... We should jump now!")
            return (1, False)
        return (0, False)
