
from .hybrid_result import HybridResult
from .hybrid_point import HybridPoint
from input.input_signal import InputSignal

from collections import defaultdict
from typing import List, Sequence, Any, Callable, Tuple, cast
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle


class HybridResultPlotter:
    """Class to plot hybrid result data, works as a wrapper around matplotlib
    Attributes:
        data (Sequence[HybridResult]): the list of sim results (themselves often a list) to plot
        optional_data (Any): optional data to plot along with the sequence of hybrid results
        _color_map (Unknown): the matplotlib colormap to use when coloring jumps
    """
    data: Sequence[HybridResult]
    optional_data: Any
    _color_map = mpl.colormaps["plasma"] #type: ignore this works actually
    
    def __init__(self, data_to_plot:Sequence[HybridResult], optional_data:Any=None):
        self.data = data_to_plot
        self.optional_data = optional_data

    def plot_state_over_time(self, state_labels:List[str], chart_label:str):
        """Take the provided data, and plot every single dimension
           of state over time. Color based on jumps.
        Args:
            state_labels (List[str]): list of labels for each dimension of the solution state
            chart_label (str): the label to give the entire chart
        """
        fig = plt.figure(layout="constrained")
        fig.suptitle(chart_label)
        solution_to_plot:List[HybridPoint] = self.data[0].sim_result

        state_dim = len(solution_to_plot[0].state)
        # set up subgraphs
        for dim, label in zip(range(state_dim), state_labels):
            fig.add_subplot(state_dim, 1, dim + 1) #type: ignore matplotlib's types are wonktastic
            fig.axes[-1].set_xlabel("Time")
            fig.axes[-1].set_ylabel(label)
        
        solution_by_jumps, plt_color_indices = self._organize_by_jumps(solution_to_plot, lambda point: point.time)

        for idx, ax in enumerate(fig.axes):
            for jump, slice in solution_by_jumps.items():
                x_data = [float(point.time) for point in slice]
                y_data = [float(point.state[idx]) for point in slice]
                ax.plot(x_data, y_data, color=self._color_map.colors[plt_color_indices[jump]], label=f"Jump {jump}")
            
            # just for one graph. trying to figure out legend placement is ruining me
            if(idx == 0):
                ax.legend()
    
        plt.show()

    def plot_state_and_input_over_time(self, state_labels:List[str], chart_label:str):
        fig = plt.figure(layout="constrained")
        fig.suptitle(chart_label)
        solution_to_plot:List[HybridPoint] = self.data[0].sim_result
        # FIXME: gotta update this, this cast is _real loose_
        input_to_plot:InputSignal = cast(InputSignal, self.data[0].input_sequence)

        state_dim = len(solution_to_plot[0].state) + 1
        # set up subgraphs for state
        for dim, label in zip(range(state_dim), state_labels + ["Actual Input"]):
            fig.add_subplot(state_dim, 1, dim + 1) #type: ignore matplotlib's types are wonktastic
            fig.axes[-1].set_xlabel("Time")
            fig.axes[-1].set_ylabel(label)
        
        solution_by_jumps, plt_color_indices = self._organize_by_jumps(solution_to_plot, lambda point: point.time)

        for idx, ax in enumerate(fig.axes):
            if idx < len(solution_to_plot[0].state):
                for jump, slice in solution_by_jumps.items():
                    x_data = [float(point.time) for point in slice]
                    y_data = [float(point.state[idx]) for point in slice]
                    ax.plot(x_data, y_data, color=self._color_map.colors[plt_color_indices[jump]], label=f"Jump {jump}")
                # just for one graph. trying to figure out legend placement is ruining me
                if(idx == 0):
                    ax.legend()
            else:
                x_data = [float(sample[0]) for sample in input_to_plot]
                y_data = [float(sample[1]) for sample in input_to_plot]
                ax.plot(x_data, y_data)
    
        plt.show()
        #fig.show()
        #  
    def plot_state_over_state(self, x_dim_idx:int, y_dim_idx:int, x_label:str, y_label:str, chart_label:str):
        """Plot two aspects of state against each other. Plots every result in self.data on the same graph.
           Colors by jumps
        Args:
            x_dim_idx (int): which dimension from state to graph on the x axis
            y_dim_idx (int): which dimension from state to graph on the y axis
            x_label (str): x-axis label
            y_label (str): y-axis label
            chart_label (str): chart label 
        """
        fig = plt.figure(layout="constrained")
        fig.suptitle(chart_label)
        ax = fig.add_subplot() #type: ignore
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        for solution in self.data:
            data_to_plot = solution.sim_result

            data_by_jumps, jump_color_map = self._organize_by_jumps(data_to_plot, lambda point: point.state[x_dim_idx])
            for jump, slice in data_by_jumps.items():
                x_data = [float(point.state[x_dim_idx]) for point in slice]
                y_data = [float(point.state[y_dim_idx]) for point in slice]
                ax.plot(x_data, y_data, color=self._color_map.colors[jump_color_map[jump]], label=f"Jump {jump}")

        ax = self._plot_level(ax)
        ax.legend() 
        plt.show()

    def plot_reachability(self, x_dim_idx:int, y_dim_idx:int, x_label:str, y_label:str, chart_label:str):
        """ Plot the results of a reachability sim-- what parts of the space can the start state get to?
            bounds are drawn in blue, failed runs are drawn in red.
        Args:
            x_dim_idx (int): which dimension from state to graph on the x axis
            y_dim_idx (int): which dimension from state to graph on the y axis
            x_label (str): x-axis label
            y_label (str): y-axis label
            chart_label (str): chart label
        """
        fig = plt.figure(layout='constrained')
        fig.suptitle(chart_label)

        # set up subgraphs
        ax = fig.add_subplot() #type: ignore matplotlib be crazy
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        # do all the solution plotting
        for run_idx in range(0, len(self.data)):
            ax = self._plot_reachability_run(run_idx, x_dim_idx, y_dim_idx, ax, plot_failure=True)

        # do the level plotting
        ax = self._plot_level(ax)

        plt.show()

    def _plot_reachability_run(self, run_idx:int, x_dim_idx:int, y_dim_idx:int, ax, plot_failure=False):
        """ Plot the results of a run from a reachability simulation. Assumes self.data came from such
            a run.
        Args:
            run_idx (int): run in self.data to graph
            x_dim_idx (int): which dimension from state to graph on the x axis
            y_dim_idx (int): which dimension from state to graph on the y axis
            ax (Axes): matplotlib axes to graph on
            plot_failure (bool): if we should plot failed runs or not
        Returns:
            ax (Axes): the axes with the run graphed on them
        """
        run = self.data[run_idx]
        output = run.sim_result
        x_data = [point.state[x_dim_idx] for point in output]
        y_data = [point.state[y_dim_idx] for point in output]
        #print(x_data)
        #print(y_data)
        if run.successful:
            ax.plot(
                x_data,
                y_data,
                "-", color="blue", label="safe bound")
        else:
            if plot_failure:
                # add a little x
                ax.plot(x_data, y_data, '--', color='red', label="death")
                ax.plot([x_data[-1]], [y_data[-1]], "x", color='red')

        handles, labels = ax.get_legend_handles_labels()
        handles_to_graph = []
        labels_to_use = []
        try:
            first_safe_idx = labels.index("safe bound")
            handles_to_graph.append(handles[first_safe_idx])
            labels_to_use.append(labels[first_safe_idx])
        except ValueError:
            pass

        try:
            first_death_idx = labels.index("death")
            handles_to_graph.append(handles[first_death_idx])
            labels_to_use.append(labels[first_death_idx])
        except ValueError:
            pass

        ax.legend(handles_to_graph, labels_to_use)
        return ax

    @classmethod
    def _evenly_divide(cls, num_samples:int, lower:float=0, upper:float=float("inf")) -> List[float]:
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
    
    @classmethod
    def _organize_by_jumps(cls, hybrid_points:Sequence[HybridPoint], sort_by:Callable) -> Tuple[defaultdict, List]:
        """Given a sequence of hybrid points, organize them by jump such that
            0: [the slice of points with no prior jumps]
            1: [the slice of points with one prior jump]
            ...
            Then evenly divide our color space by the number of jumps so we can give each slice a 
            unique color.
        Args:
            hybrid_points (Sequence[HybridPoint]): the hybrid points to break up
            sort_by (Callable): a function that takes in one hybrid point and returns the value to
                                sort each slice by
        """
        data_by_jumps = defaultdict(list)
        for point in hybrid_points:
            data_by_jumps[point.jumps].append(point)
        for num_jumps, points in data_by_jumps.items():
            data_by_jumps[num_jumps] = sorted(points, key=sort_by) 
    
        color_idxs = cls._evenly_divide(
            max([n_jumps for n_jumps in data_by_jumps.keys()]) + 1, 0, len(cls._color_map.colors)
        )
        return data_by_jumps, color_idxs
    
    def _plot_level(self, ax):
        """ Plot optional data as a level.
            This is very experimental and probably won't live here forever
        Args:
            ax (Axes): matplotlib axes to plot on
        Returns:
            Axes: the same matplotlib axes, just modified
        """
        if self.optional_data:
            for obstacle in self.optional_data.obstacles: #type: ignore (not dealing with the pol)
                width = obstacle[1][0] - obstacle[0][0]
                height = obstacle[1][1] - obstacle[0][1]

                ax.add_patch(Rectangle(obstacle[0], width, height))
        return ax

            

            


