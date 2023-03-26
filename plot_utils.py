import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
import math
from collections import defaultdict
from pprint import pformat, pprint

# what if we could graph stuff




def plot_solutions(solutions, dim_0, dim_1, ax: Axes):
    """Given a bunch of solutions, state dimensions to plot and and axis to plot them on,
    graph it!
    """
    good_artist_idx = 0
    bad_artist_idx = 0
    for solution in solutions:
        good = solution.successful
        input = solution.input_sequence
        output = solution.sim_result
        t = [point.time for point in output]
        y = [point.state for point in output]
        j = [point.jumps for point in output]
        input_signal = [sample[1] for sample in input]
        # we want to plot y[dim_0] against y[dim_1]
        plt_pair = tuple([[], []])
        for t_idx, t_val in enumerate(t):
            state_at_t = y[t_idx]
            plt_pair[0].append(state_at_t[dim_0])
            plt_pair[1].append(state_at_t[dim_1])
        if good:
            ax.plot(plt_pair[0], plt_pair[1], "-", color="blue", label="safe bound")
        else:
            pass
            # add a little x
            ax.plot(plt_pair[0], plt_pair[1], '--', color='red', label="death")
            ax.plot([plt_pair[0][-1]], [plt_pair[1][-1]], "x", color='red')

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


def plot_solutions_combined(
    solution_list, level, dim_0, dim_1, label_0, label_1, chart_label
):
    """Combine a bunch of solutions together into one unified plot"""
    fig = plt.figure(layout='constrained')
    fig.suptitle(chart_label)
    # color_map = mpl.colormaps['plasma']  # type: ignore

    # set up subgraphs
    ax = fig.add_subplot()
    ax.set_xlabel(label_0)
    ax.set_ylabel(label_1)

    # do all the solution plotting
    for solutions in solution_list:
        ax = plot_solutions(solutions, dim_0, dim_1, ax)

    # do the level plotting
    for obstacle in level.obstacles:
        width = obstacle[1][0] - obstacle[0][0]
        height = obstacle[1][1] - obstacle[0][1]

        ax.add_patch(Rectangle(obstacle[0], width, height))
    
    plt.show()
