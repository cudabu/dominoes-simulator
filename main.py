# main.py
import argparse
from itertools import cycle, islice
from simulation import run_simulation
from results import print_results
from strategies import (
    LongestPathStrategy,
    RandomPathStrategy,
    GreedyStrategy,
    RandomStrategy,
)

# Recommended domino set per player count (official Mexican Train ruleset)
RECOMMENDED_SET = {
    2: 9,  3: 9,
    4: 12, 5: 12, 6: 12, 7: 12, 8: 12,
    9: 15, 10: 15, 11: 15, 12: 15,
    13: 18, 14: 18,
}

parser = argparse.ArgumentParser(description="Run a Mexican Train dominoes simulation.")
parser.add_argument(
    "--players", type=int, default=4, metavar="N",
    choices=range(2, 15),
    help="Number of players (2-14, default 4)",
)
parser.add_argument(
    "--games", type=int, default=500,
    help="Number of games to simulate (default 500)",
)
args = parser.parse_args()

max_pip = RECOMMENDED_SET[args.players]

strategy_types = [LongestPathStrategy, RandomPathStrategy, GreedyStrategy, RandomStrategy]
strategies = [cls() for cls in islice(cycle(strategy_types), args.players)]

result = run_simulation(strategies, num_games=args.games, max_pip=max_pip)
print_results(result)
