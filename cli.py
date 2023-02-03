"""Run our prototypes as part of a cli!
"""
import argparse
import random
from flappy.flappy_simulation import FlappySim
from plot_utils import plot_position, plot_solutions_combined


def single_run(args) -> None:
    """Perform a single run of Flappy
    Args:
         args (Namespace): command line arguments from argparse
    """
    sample_rate = args.sample_rate
    samples = args.samples
    seed = args.seed

    random.seed(seed)
    # derive the end time from the provided samples + sampling rate
    num_samples = len(samples)
    max_t = num_samples * sample_rate

    sim = FlappySim(max_t, sample_rate, seed)
    result = sim.single_run(samples)
    plot_position(result, sim.level, 0, 1, "X Pos", "Y Pos", "Flappy Position")


def find_reachability_bounds(args) -> None:
    """Do a reachability analysis of Flappy, looking for the upper and
    lower bound.
    """
    max_t = args.max_time
    num_samples = args.num_samples
    sample_rate = args.sample_rate
    seed = args.seed

    random.seed(seed)
    # handle invalid args
    if max_t is None and num_samples is None:
        raise ValueError("Need to specify a max_time or num_samples!")

    # derive max time
    if num_samples:
        max_t = num_samples * sample_rate

    sim = FlappySim(max_t, sample_rate, seed)
    results = sim.reachability_simulation()
    plot_solutions_combined(
        results, sim.level, 0, 1, "X Pos", "Y Pos", "Flappy Position"
    )


def build_cli_parser() -> argparse.ArgumentParser:
    """Return a command line argument parser for Flappy analysis.
    The README has more information.
    """
    parser = argparse.ArgumentParser(
        prog="FlappySim", description="A Hybrid Automata Simulation of Flappy Bird"
    )
    parser.add_argument(
        "-r",
        "--sample_rate",
        type=float,
        help="How often the sim should sample input signal",
        default=1 / 60,
    )
    parser.add_argument(
        "-d",
        "--seed",
        type=int,
        help="Level generation seed",
        default=random.randint(0, 10000),
    )
    subparser = parser.add_subparsers(
        description="Subparsers for handling analysis tasks"
    )
    single_parser = subparser.add_parser("single", help="For doing single runs")
    bounds_parser = subparser.add_parser(
        "reachability", help="For finding reachability bounds"
    )

    single_parser.add_argument(
        "-s",
        "--samples",
        type=int,
        nargs="*",
        help="Specify a list of sample values directly",
    )

    bounds_number_of_samples_group = bounds_parser.add_mutually_exclusive_group()
    _add_common_arguments_to_group(bounds_number_of_samples_group)

    # single run stuff
    single_parser.set_defaults(func=single_run)
    # bounds run stuff
    bounds_parser.set_defaults(func=find_reachability_bounds)

    return parser


def _add_common_arguments_to_group(group):
    group.add_argument(
        "-n",
        "--num_samples",
        type=int,
        help="Say exactly how many samples we want for this run",
    )
    group.add_argument(
        "-m",
        "--max_time",
        type=float,
        help="How long we want the sim to run, \
            samples will be evenly spaced from 0 to max_time",
    )


if "__main__" == __name__:
    # parse arguments
    parser = build_cli_parser()
    args: argparse.Namespace = parser.parse_args()
    args.func(args)

# running our model on some different resolutions
# run_model(0.3, 1/60) # 60 fps
# run_model(0.6, 1/30) # 30 fps
# run_model(1.2, 1/15) # 15 fps
# find_top_reachability(1.2, 1/15)
# reachability_analysis(1.2, 1/15)
# run_model(1.2, 1/15) # 15 fps
