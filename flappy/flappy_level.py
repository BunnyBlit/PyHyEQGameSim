""" Object for handling ye flappy level. A flappy level is just a few rectangular blocks
    and two limits on y position
"""
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class FlappyLevel:
    """A level for Flappy
    Attributes:
        obstacles: List[Tuple[Tuple[float, float], Tuple[float,float]]]:
                                                    each obstacle is a rectangle represented by
                                                    it's bottom left and top right point
        # FIXME: that  type is terrible, maybe formalize it into a dataclass?
        lower_bound (float): the lowest part of the level our bird can go
        upper_bound (float): the highest part of a level our bird can go
        pipe_width (Optional[float]): for procedural gen, how wide should the pipes be
        gap (Optional[float]): for procedural gen, how big should the virtical gap between pipes be
        seed (Optional[int]): for procedural gen, generation seed
    """

    obstacles: List[Tuple[Tuple[float, float], Tuple[float, float]]]
    upper_bound: float
    lower_bound: float
    pipe_width: Optional[float] = None
    gap: Optional[float] = None
    seed: Optional[int] = None

    @classmethod
    def simple_procedural_gen(cls, seed: Optional[int]):
        """run a simple procedure for making a sample flappy bird level
        Args:
            seed (Optional[int]): generation seed
        Returns:
            FlappyLevel: a new level to use
        """
        lower_bound: float = 0.0
        upper_bound: float = 5.0
        x_start: float = 1.0
        x_period: float = 2.0
        heights: List[float] = [2, 1.5, 1]

        pipe_width: float = 0.7
        gap: float = 1.0
        num_gaps: int = 6  # total pipes placed is 2x this number

        pipes = []
        for i in range(num_gaps):
            left_base = x_start + x_period * i
            bottom_height = random.choice(heights)
            top_start = gap + bottom_height
            # lower pipe
            pipes.append(
                ((left_base, lower_bound), (left_base + pipe_width, bottom_height))
            )
            # upper pipe
            pipes.append(
                ((left_base, top_start), (left_base + pipe_width, upper_bound))
            )

        return FlappyLevel(pipes, 5.0, 0.0, pipe_width, gap, seed=seed)

    @classmethod
    def scripted_gen_level(cls):
        """A function to edit to generate a very particular level to test
           degenerate cases.
        Returns:
           FlappyLevel: a handcrafted, artisanal Flappy Level
        """
        # lower left corner, upper right corner
        scripted_obstacles = [((2.0, 0.0), (2.5, 2.0)), ((1.25, 4.0), (1.75, 5.0))]
        return FlappyLevel(scripted_obstacles, 5.0, 0.0)
