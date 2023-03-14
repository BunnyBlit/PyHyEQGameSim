import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
import math
from pprint import pformat, pprint

# what if we could graph stuff


def spaced_samples(lower, upper, num_samples):
    return [
        math.floor(lower + x * (upper - lower) / num_samples)
        for x in range(num_samples)
    ]


def plot_state_over_time(solution, state_labels, chart_label):
    """Solution is three lists:
    t: times
    y: state at times
    j: number of jumps at the following time
    """
    fig = plt.figure(layout='constrained')
    fig.suptitle(chart_label)
    t = [point.time for point in solution.sim_result]
    y = [point.state.to_list() for point in solution.sim_result]
    j = [point.jumps for point in solution.sim_result]
    state_dim = len(y[0])
    axs = []
    color_map = mpl.colormaps["plasma"]  # type: ignore this works, actually
    # set up subgraphs
    for dim, label in zip(range(state_dim), state_labels):
        axs.append(fig.add_subplot(state_dim, 1, dim + 1))
        axs_current = axs[-1]
        axs_current.set_xlabel("Time")
        axs_current.set_ylabel(label)

    for idx, ax in enumerate(axs):
        # divide into breaks based on color
        plt_slices = {}
        # this is nasty, but I'm making ranges
        # of each value under a unique j:
        # 0: (t where j=0, y[plt_idx] where j=0, 0),
        # 1: (t where j=1, y[plt_idx] where j=1, 1),
        # ...
        for t_idx, t_i in enumerate(t):
            y_i = y[t_idx]
            j_i = j[t_idx]
            if j_i not in plt_slices:
                plt_slices[j_i] = ([], [], j_i)
            plt_slices[j_i][0].append(t_i)
            plt_slices[j_i][1].append(y_i[idx])
    
        # map each j value to something that'll fit in our color map
        plt_color_indices = spaced_samples(
            0, len(color_map.colors), j[-1] + 1
        )  # j is 0 indexed
        for j_i, slice in plt_slices.items():
            ax.plot(slice[0], slice[1], color=color_map.colors[plt_color_indices[j_i]], label=f"Jump {j_i}")
        
        # just for one graph. trying to figure out legend placement is ruining me
        if(idx == 0):
            ax.legend()
        
    plt.show()
    # fig.show()


def plot_state_relation(solution, level, dim_0, dim_1, label_0, label_1, chart_label):
    """Plot any two parts of the solution against each other"""
    fig = plt.figure(layout='constrained')
    fig.suptitle(chart_label)
    input = solution.input_sequence

    output = solution.sim_result
    t = [point.time for point in output]
    y = [point.state.to_list() for point in output]
    j = [point.jumps for point in output]
    color_map = mpl.colormaps["plasma"]  # type: ignore

    # set up subgraphs
    ax = fig.add_subplot()
    ax.set_xlabel(label_0)
    ax.set_ylabel(label_1)

    # divide into breaks based on color
    plt_slices = {}
    # this is nasty, but I'm making ranges
    # of each value under a unique j:
    # 0: (t where j=0, y[plt_idx] where j=0, 0),
    # 1: (t where j=1, y[plt_idx] where j=1, 1),
    # ...
    for t_idx, t_i in enumerate(t):
        y_i = y[t_idx]
        j_i = j[t_idx]
        if j_i not in plt_slices:
            plt_slices[j_i] = ([], [], j_i)
        plt_slices[j_i][0].append(y_i[dim_0])
        plt_slices[j_i][1].append(y_i[dim_1])

    # now adjust-- we need to put the last element in plt_slices[N] on the end of plt_slices[N-1]
    # so we can draw complete lines
    # TODO: fun fact: this breaks for high state numbers
    for slice_idx in range(max(plt_slices.keys()), min(plt_slices.keys()), -1):
        plt_slices[slice_idx - 1][0].append(plt_slices[slice_idx][0][0])
        plt_slices[slice_idx - 1][1].append(plt_slices[slice_idx][1][0])

    # map each j value to something that'll fit in our color map
    plt_color_indices = spaced_samples(
        0, len(color_map.colors), j[-1] + 1
    )  # j is 0 indexed
    for j_i, slice in plt_slices.items():
        ax.plot(slice[0], slice[1], color=color_map.colors[plt_color_indices[j_i]])

    # plot obstacles
    if level:
        for obstacle in level.obstacles:
            width = obstacle[1][0] - obstacle[0][0]
            height = obstacle[1][1] - obstacle[0][1]

            ax.add_patch(Rectangle(obstacle[0], width, height))
    
    # fig.show()
    plt.show()


def plot_all_positions(solutions, level, dim_0, dim_1, label_0, label_1, chart_label):
    """plot every attempt that the sim made
    we lose color info on jumps here, but that's ok because
    we're just looking for the end position of each run
    """
    fig = plt.figure(layout='constrained')
    fig.suptitle(chart_label)
    # color_map = mpl.colormaps['plasma']  # type: ignore

    # set up subgraphs
    ax = fig.add_subplot()
    ax.set_xlabel(label_0)
    ax.set_ylabel(label_1)

    for solution in solutions:
        good, output, input = solution
        t = [point.time for point in output]
        y = [point.state.to_list() for point in output]
        j = [point.jumps for point in output]
        input_signal = [sample[1] for sample in input]
        # we want to plot y[dim_0] against y[dim_1]
        plt_pair = tuple([[], []])
        for t_idx, t_val in enumerate(t):
            state_at_t = y[t_idx]
            plt_pair[0].append(state_at_t[dim_0])
            plt_pair[1].append(state_at_t[dim_1])
        if good:
            ax.plot(plt_pair[0], plt_pair[1], "-", color="blue")
            # print(f"Good: {input_signal}")
            # last_point = (plt_pair[0][-1], plt_pair[1][-1])
            # annotate_point = (last_point[0] - 1.4, last_point[1] - 0.5)
            # ax.annotate(f"{input_signal}", last_point, annotate_point)
        else:
            ax.plot(plt_pair[0], plt_pair[1], "--", color="red")
            last_solve_point_time = t[-1]
            relevant_input_signal = [
                value for time, value in input if time <= last_solve_point_time
            ]
            # print(f"Last solution time: {t[-1]}")
            # print(f"Bad: {relevant_input_signal}")

    # plot obstacles
    for obstacle in level.obstacles:
        width = obstacle[1][0] - obstacle[0][0]
        height = obstacle[1][1] - obstacle[0][1]

        ax.add_patch(Rectangle(obstacle[0], width, height))
    
    plt.show()


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
        y = [point.state.to_list() for point in output]
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
