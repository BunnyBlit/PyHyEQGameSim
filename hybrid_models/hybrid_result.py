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
