"""Dataclass for a hybrid simulation result, pairs input with output.
   Input is optional: some hybrid systems have no input, most of the ones I'm looking
   at do.
"""
from typing import Optional, Any, List
from dataclasses import dataclass
from .hybrid_point import HybridPoint
from input.input_signal import InputSignal
@dataclass
class HybridResult():
    successful:bool
    input_sequence: Optional[InputSignal] #TODO: formalize how input works a little more. It's a value + a time?
    sim_result: List[HybridPoint]
