
from .hybrid_result import HybridResult
from .hybrid_point import HybridPoint
from collections import defaultdict
from typing import List, Sequence
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle


class HybridResultPlotter:
    """Class to plot hybrid result data, works as a wrapper around matplotlib
    """
    data: Sequence[HybridResult]

    def __init__(self, data_to_plot:Sequence[HybridResult]):
        self.data = data_to_plot

    def _evenly_divide(self, num_samples:int, lower:float=0, upper:float=float("inf")) -> List[float]:
        """Evenly divide the lower, upper range by num_samples
        Args:
            num_samples (int): the number of evenly spaced samples to get from the range
            lower (float): lower bound to sample. Only tested with 0
            upper (float): upper bound to sample.
        Returns:
            List[float]: a list with len(num_samples), evenly spaced from lower to upper
        """
        return [
            math.floor(lower + x * (upper - lower) / num_samples)
            for x in range(num_samples)
        ]

    def plot_state_over_time(self, state_labels, chart_label):
        """Solution is three lists:
        """
        fig = plt.figure(layout="constrained")
        fig.suptitle(chart_label)
        solution_to_plot:List[HybridPoint] = self.data[0].sim_result

        state_dim = len(solution_to_plot[0].state)
        color_map = mpl.colormaps["plasma"]  # type: ignore this works, actually
        # set up subgraphs
        for dim, label in zip(range(state_dim), state_labels):
            new_ax = fig.add_subplot(state_dim, 1, dim + 1)
            fig.axes[-1].set_xlabel("Time")
            fig.axes[-1].set_ylabel(label)
        
        solution_by_jumps = defaultdict(list)
        for point in solution_to_plot:
            solution_by_jumps[point.jumps].append(point)
        for num_jumps, points in solution_by_jumps.items():
            solution_by_jumps[num_jumps] = sorted(points, key=lambda point: point.time)
        
        # map each j value to something that'll fit in our color map
        plt_color_indices = self._evenly_divide(
            max([n_jumps for n_jumps in solution_by_jumps.keys()]) + 1, 0, len(color_map.colors)
        )
        for idx, ax in enumerate(fig.axes):
            for jump, slice in solution_by_jumps.items():
                x_data = [float(point.time) for point in slice]
                y_data = [float(point.state[idx]) for point in slice]
                ax.plot(x_data, y_data, color=color_map.colors[plt_color_indices[jump]], label=f"Jump {jump}")
            
            # just for one graph. trying to figure out legend placement is ruining me
            if(idx == 0):
                ax.legend()
   
        plt.show()
        #fig.show()

