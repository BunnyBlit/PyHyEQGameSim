""" Model input as a sampled single, where we track values along with sample times
"""

from dataclasses import dataclass
from typing import List, Union, Iterable


@dataclass
class InputSignal(Iterable):
    """This class models input from a button, joystick, etc, as a sampled signal
    where each value of the input thing corresponds with a time that it has that
    value at
    """

    samples: Union[List[int], List[float]]
    times: List[float]
    label: str = "No Label Provided"
    _idx: int = 0  # so we can be an iterator

    def __iter__(self):
        self._idx = -1  # I know. it makes the next logic much cleaner
        return self

    def __next__(self):
        """iterator pattern is time, sample"""
        if self._idx < len(self.samples) - 1 and self._idx < len(self.times) - 1:
            self._idx += 1
            return (self.times[self._idx], self.samples[self._idx])
        else:
            raise StopIteration
