"""Dataclass for a hybrid simulation result, pairs input with output.
   Input is optional: some hybrid systems have no input, but most do
   for video games.
"""
from typing import Optional, List
from dataclasses import dataclass
from .hybrid_point import HybridPoint
from input.input_signal import InputSignal


@dataclass
class HybridResult:
    """Dataclass for a result from a Hybrid Equations simulation.
    Attributes:
        successful (bool): did the sim terminate successfully or not
        input_sequence (InputSignal): the input to the system over time
        sim_result (List[HybridPoint]): results of the simulation at each time step
    """
    successful: bool
    input_sequence: Optional[
        InputSignal
    ]
    sim_result: List[HybridPoint]

    def __str__(self) -> str:
        """Human readable representation of this solution"""
        str_rep:str = ""
        for hybrid_point in self.sim_result:
            str_rep += f"{hybrid_point.time:0.004f}\t{hybrid_point.state}\t{hybrid_point.jumps}\n"

        return str_rep
        

