"""A bouncing ball state! As a list serializable class
"""
from hybrid_models.ndarray_dataclass import NDArrayBacked
from collections.abc import Sequence

class BallState(NDArrayBacked[float]):
    """State of a bouncing ball! We only care about one dimension,
        we're not worried about left/right position for a demo
    Properties:
        y_pos (float): y position
        y_vel (float): y velocity
    """

    @property
    def y_pos(self) -> float:
        return self._data[0]
    
    @y_pos.setter
    def y_pos(self, value:float):
        self._data[0] = value

    @property
    def y_vel(self) -> float:
        return self._data[1]
    
    @y_vel.setter
    def y_vel(self, value:float):
        self._data[1] = value

    @classmethod
    def from_properties(cls, y_pos:float, y_vel:float):
        return cls([y_pos, y_vel])