""" Model input as a sampled signal, where we track values
    along with sample times
"""

from dataclasses import dataclass
from typing import List, Union, Iterable, Tuple


@dataclass
class InputSignal(Iterable):
    """This class models input from a button, joystick, etc, as a sampled
       signal where each value of the input thing corresponds with a
       time.
       Parameters:
           samples (List[int|float]): the actual value of the samples
           times (List[float]): the times that each sample ocurred at
           label (str): signal label
    """

    samples: List[int | float]
    times: List[float]
    label: str = "No Label Provided"
    _idx: int = 0  # so we can be an iterator

    def __iter__(self):
        """ Iterator protocol initialization.
        Start at -1 here to make __next__ have some nicer logic.
        """
        self._idx = -1  # I know. it makes the next logic much cleaner
        return self

    def __next__(self):
        """Iterator for the next time, sample pair"""
        if self._idx < len(self.samples) - 1 and \
                self._idx < len(self.times) - 1:
            self._idx += 1
            return (self.times[self._idx], self.samples[self._idx])
        else:
            raise StopIteration
    
    def __getitem__(self, key:int | slice)-> Tuple[float, int | float] | List[Tuple[float, int | float]]:
        """ Direct access to samples so we don't need to run through
            the whole signal. Supports slicing and single element access
            TODO: this is a sin
        """
        if isinstance(key, int):
            return (self.times[key], self.samples[key])
        elif isinstance(key, slice):
            return [(time, sample) for time, sample in zip(self.times[key], self.samples[key])]

    def __str__(self) -> str:
        """ For pretty printing of signals
        """
        print_str = ""
        for time, sample in zip(self.samples, self.times):
            print_str += f"{time:0.04f}\t{sample:0.04f}\n"
        return print_str