"""Run our prototypes as part of a cli!
"""
import argparse
import random
from flappy.flappy_simulation import FlappySim
from ball_bounce.ball_simulation import BallSim
from plot_utils import plot_state_relation, plot_state_over_time, plot_solutions_combined


def single_flappy_run(args) -> None:
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
    plot_state_relation(result, sim.level, 0, 1, "X Pos", "Y Pos", "Flappy Position")

def single_ball_run(args) -> None:
    """Perform a single run of a bouncing ball
    Args:
        args (Namespace): command line arguments from argparse for bouncing ball
    """
    max_t = args.max_time
    sim = BallSim(max_t)
    result = sim.single_run()
    plot_state_over_time(result, ["Y Pos", "Y Vel"], "Ball Height")

def find_flappy_reachability_bounds(args) -> None:
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
    """Build out a complex tree of subparsers for handling various
        analysis tasks for various models that we have in the repository
        README either does or will have information!
    """
    parser = argparse.ArgumentParser(
        prog="FlappySim", description="A Hybrid Automata Simulation of Flappy Bird"
    )
    model_parsers = parser.add_subparsers(
        description="Subparsers for which model we're running on"
    )
    # ball time
    ball_parser = model_parsers.add_parser("ball", help="For simulating the simple Bouncing Ball example!")
    ball_analysis_parsers = ball_parser.add_subparsers(
        description="Subparsers for handling analysis tasks"
    )
    single_ball_parser = ball_analysis_parsers.add_parser("single", help="For doing single runs")
    _add_max_time_argument(single_ball_parser)

    # flappy time
    flappy_parser = model_parsers.add_parser("flappy", help="For simulating Flappy Bird!")
    flappy_analysis_parsers = flappy_parser.add_subparsers(
        description="Subparsers for handling analysis tasks"
    )
    # single runs
    single_flappy_parser = flappy_analysis_parsers.add_parser("single", help="For doing single runs")
    _add_sample_rate(single_flappy_parser)
    _add_seed(single_flappy_parser)
    single_flappy_parser.add_argument(
        "-s",
        "--samples",
        type=int,
        nargs="*",
        help="Specify a list of sample values directly",
    )

    # reachability analysis
    reachability_flappy_parser = flappy_analysis_parsers.add_parser(
        "reachability", help="For finding reachability bounds"
    )
    _add_sample_rate(reachability_flappy_parser)
    _add_seed(reachability_flappy_parser)
    bounds_number_of_samples_group = reachability_flappy_parser.add_mutually_exclusive_group()
    _add_max_time_argument(bounds_number_of_samples_group)
    _add_num_samples_argument(bounds_number_of_samples_group)

    # single run of bouncing ball
    single_ball_parser.set_defaults(func=single_ball_run)
    # single run flappy
    single_flappy_parser.set_defaults(func=single_flappy_run)
    # bounds run flappy
    reachability_flappy_parser.set_defaults(func=find_flappy_reachability_bounds)

    return parser


def _add_max_time_argument(parse_obj):
    """ Add a max time object to a parsing object that implements the
        add_argument function
    """
    parse_obj.add_argument(
        "-m",
        "--max_time",
        type=float,
        help="How long we want the sim to run, \
            if this model is sampling input, \
            samples will be evenly spaced from 0 to max_time",
    )

def _add_num_samples_argument(parse_obj):
    """ Add the number of samples argument to a parsing object that
        implements the add_argument function
    """
    parse_obj.add_argument(
        "-n",
        "--num_samples",
        type=int,
        help="Say exactly how many samples we want for this run",
    )

def _add_sample_rate(parse_obj):
    """ Add the sample rate argument to a parsing object that
        implements the add_argument function
    """
    parse_obj.add_argument(
        "-r",
        "--sample_rate",
        type=float,
        help="How often the sim should sample input signal",
        default=1 / 60,
    )

def _add_seed(parse_obj):
    """ Add the seed argument to a parsing object that implements
        the add_arguments function
    """
    parse_obj.add_argument(
        "-d",
        "--seed",
        type=int,
        help="Level generation seed",
        default=random.randint(0, 10000),
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
