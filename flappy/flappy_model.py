""" Hybrid model for flappy bird
"""
from typing import List, Tuple
from hybrid_models.hybrid_model import HybridModel
from hybrid_models.hybrid_point import HybridPoint
from input.input_signal import InputSignal
from .flappy_state import FlappyState
from .flappy_params import FlappyParams
from .flappy_level import FlappyLevel

class FlappyModel(HybridModel[FlappyState, FlappyParams]):
    """ It's a hybrid model for flappy bird! Implements the 4 big functions for hybrid models,
        as well as a way to get input. For flappy, input is a single button 0 (off) or 1 (on)
        Flappy also takes an input sequence via an optional input_sequence parameter
    """
    def __init__(self, start_state:FlappyState, system_params:FlappyParams, level:FlappyLevel, t_max:float=2.0, j_max:int=8, input_sequence:InputSignal=InputSignal([],[])):
        """Constructor
        """
        super().__init__() # hybrid models don't define constructors... for now
        self.input_sequence:InputSignal = input_sequence
        self.j_max=j_max
        self.t_max=t_max
        self.start_state=start_state
        self.system_params=system_params
        self.state_factory=FlappyState
        self.level = level

    def get_input(self, time: float, jumps: int) -> int:
        """ get input for ye flappy bird. We expect all the input for this simulation run to be already
            calculated by the time we get to this point
            # FIXME: this still works on a precalculated input, which may not be right
            This function returns an int because that's what our input is-- a 1 button on/off signal.
        """
        if not self.input_sequence:
            raise RuntimeError("Need to set an input sequence before getting input!")
 
        samples_with_distance_to_now = [(sample_time, sample, abs(time - sample_time))
                                    for sample_time, sample in self.input_sequence]
        samples_with_distance_to_now.sort(key=lambda elem: elem[2])
        sample = samples_with_distance_to_now[0] 
        return int(sample[1])

    def check_collisions(self, state:FlappyState) -> bool:
        """ Check to see if we're colliding with anything. For flappy, this should
            stop everything.
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
            if state.x_pos >= bottom_left_coord[0] and \
                state.x_pos <= top_right_coord[0] and \
                state.y_pos >= bottom_left_coord[1] and \
                state.y_pos <= top_right_coord[1]:
                return True

        return False

    def flow(self, hybrid_state:HybridPoint[FlappyState]) -> FlappyState:
        """ Flow function! This should take in y and return dy/dt.
        Args:
            hybrid_state: (HybridPoint[FlappyState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            FlappyState: dy/dt! The derivative of y w.r.t t given t and j and params!
        """
        state = hybrid_state.state
        # TODO: we probably want to not overwrite the state here
        if state.pressed == 0: #falling
            state.x_pos = self.system_params.pressed_x_vel
            state.y_pos = state.y_vel
            state.y_vel = -self.system_params.gamma
            state.pressed = 0
            return state
        else: #flapping (pressed == 1)
            state.x_pos = self.system_params.pressed_x_vel
            state.y_pos = self.system_params.pressed_y_vel
            state.y_vel = 0 
            state.pressed = 0
            return state

    def jump(self, hybrid_state:HybridPoint[FlappyState]) -> FlappyState:
        """ Jump function! This should return a new y after a jump, given t and j and params.
        Args:
            hybrid_state: (HybridPoint[FlappyState]): flappy's current state, along with
                                                      the current time and number of jumps
        Returns:
            FlappyState: new y after the jump!
        """
        # sample input signal
        # parameterized input signal w.r.t. time and jumps
        state = hybrid_state.state
        time = hybrid_state.time
        jumps = hybrid_state.jumps
        new_pressed = self.get_input(time, jumps)
        state.pressed = new_pressed
        # jump according to the new input signal
        if new_pressed == 1:
            state.y_vel = self.system_params.pressed_y_vel
        
        return state

    def flow_check(self, hybrid_state:HybridPoint[FlappyState]) -> Tuple[int, bool]:
        """ Flow check! This function checks if we can flow.
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

    def jump_check(self, hybrid_state:HybridPoint[FlappyState]) -> Tuple[int, bool]:
        """ Jump check! This should return 1 if we can jump, 0 otherwise
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