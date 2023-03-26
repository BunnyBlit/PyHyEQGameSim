"""Define a simple abstraction layer over a list so that we can interface with
    numpy-based abstractions a little easier
"""
from typing import List, Generic, TypeVar
from collections.abc import Sequence
from functools import singledispatch
from numpy import ndarray, array
from numpy.typing import ArrayLike
from abc import abstractmethod
from typing import Type

T = TypeVar("T")

class NDArrayBacked(Sequence, Generic[T]):
    _data:ndarray

    def __init__(self, data:ArrayLike):
        self._data = array(data)

    def __len__(self) -> int:
        return self._data.size

    def __getitem__(self, key:int) -> T:
        return self._data[key]

    def __str__(self) -> str:
        return ", ".join([f"{elem:0.04f}" for elem in self._data])

    @classmethod
    @abstractmethod
    def from_properties(cls):
        pass

    @abstractmethod
    def generate_header(self) -> Sequence[str]:
        pass