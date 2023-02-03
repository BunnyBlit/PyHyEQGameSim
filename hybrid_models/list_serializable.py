""" Abstract / Default class for model params / state. We need to be able to convert
    model state to a list so we can have it be consumed by most ODE solvers, this provides
    a simple interface to do that with
"""
from typing import List

class ListSerializable:
    """ Abstract class for a dataclass where we can return it's attributes
        as a list (serializes to a list) and can be serialized from any sequence
        This is a "empty" implementation of it
    """

    def __init__(self, *arg_list):
        """Subclasses very much need to implement this! We'd expect the
           constructor of any ListSerializable to take in the arg_list and use
           it to assign values to parameters
        """
        pass

    def to_list(self) -> List:
        """This lets us return the values in a subclasses attributes as a list
           By default, we just return an empty list.
        """
        return []