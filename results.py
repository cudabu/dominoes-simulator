# results.py
from simulation import SimulationResult


def print_results(result: SimulationResult) -> None:
    """
    Print a ranked results table for a completed simulation.

    Players are ranked by win rate (highest first), with average score
    as the tiebreaker (lowest first).
    """
    ranked = sorted(
        enumerate(result.player_results),
        key=lambda t: (-t[1].win_rate, t[1].avg_score),
    )

    COL = (5, 24, 6, 6, 5, 5)  # rank, strategy, win%, avg, min, max

    header = f"Results — {result.num_games} games | Double-{result.max_pip} | {result.num_players} players"
    print(header)
    print("─" * len(header))
    print(
        f"  {'Rank':<{COL[0]}} {'Strategy':<{COL[1]}} {'Win%':>{COL[2]}}"
        f"  {'Avg':>{COL[3]}}  {'Min':>{COL[4]}}  {'Max':>{COL[5]}}"
    )
    print(
        f"  {'─'*COL[0]} {'─'*COL[1]} {'─'*COL[2]}"
        f"  {'─'*COL[3]}  {'─'*COL[4]}  {'─'*COL[5]}"
    )

    for rank, (_, pr) in enumerate(ranked, start=1):
        print(
            f"  {rank:<{COL[0]}} {pr.strategy_name:<{COL[1]}} {pr.win_rate:>{COL[2]-1}.1f}%"
            f"  {pr.avg_score:>{COL[3]}.1f}  {pr.min_score:>{COL[4]}}  {pr.max_score:>{COL[5]}}"
        )
