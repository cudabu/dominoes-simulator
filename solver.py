# solver.py
"""
Longest-path solver for a Mexican Train hand.

Given a list of dominoes and the current open end of a personal train,
finds the longest chain that can be played in sequence, breaking ties
by highest total pip count.

Usage as a module:
    from solver import solve
    solution = solve(hand, open_end=6)
    print(solution.path)       # tiles to play on own train, in order
    print(solution.remainder)  # tiles left over for other trains

Usage as a CLI:
    python3 solver.py --open-end 6 --tiles "6-4 4-3 3-1 2-2 5-1"
"""

from dataclasses import dataclass
from domino import Domino


@dataclass
class PathSolution:
    path: list[Domino]      # tiles to play on personal train, in order
    remainder: list[Domino] # tiles left for Mexican Train / open trains
    open_end: int           # the open end after the path is fully played


def solve(dominoes: list[Domino], open_end: int) -> PathSolution:
    """
    Find the longest chain playable from open_end through the given dominoes.
    Ties in length are broken by highest total pip count.

    Returns a PathSolution with the ordered path, leftovers, and resulting open end.
    """
    path = _dfs(open_end, list(dominoes), [], [])
    path_ids = {id(d) for d in path}
    remainder = [d for d in dominoes if id(d) not in path_ids]
    final_end = _chain_end(path, open_end)
    return PathSolution(path=path, remainder=remainder, open_end=final_end)


def _dfs(
    open_end: int,
    remaining: list[Domino],
    current_path: list[Domino],
    best: list[Domino],
) -> list[Domino]:
    if _is_better(current_path, best):
        best = list(current_path)

    for domino in [d for d in remaining if d.matches(open_end)]:
        remaining.remove(domino)
        current_path.append(domino)
        best = _dfs(domino.other_end(open_end), remaining, current_path, best)
        current_path.pop()
        remaining.append(domino)

    return best


def _is_better(candidate: list[Domino], best: list[Domino]) -> bool:
    if len(candidate) > len(best):
        return True
    if len(candidate) == len(best):
        return sum(d.pip_count for d in candidate) > sum(d.pip_count for d in best)
    return False


def _chain_end(path: list[Domino], start: int) -> int:
    end = start
    for domino in path:
        end = domino.other_end(end)
    return end


def _parse_tiles(tile_str: str) -> list[Domino]:
    """Parse space-separated 'high-low' tile strings, e.g. '6-4 3-3 2-1'."""
    tiles = []
    for token in tile_str.split():
        parts = token.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid tile '{token}' — expected format: high-low (e.g. 6-4)")
        tiles.append(Domino(int(parts[0]), int(parts[1])))
    return tiles


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find the longest playable path through a domino hand.")
    parser.add_argument("--open-end", type=int, required=True, help="Current open end of your train (e.g. 6)")
    parser.add_argument("--tiles", type=str, required=True, help="Space-separated tiles in high-low format (e.g. '6-4 3-3 2-1')")
    args = parser.parse_args()

    hand = _parse_tiles(args.tiles)
    solution = solve(hand, args.open_end)

    print(f"\nOpen end:  {args.open_end}")
    print(f"Hand ({len(hand)} tiles):  {' '.join(str(d) for d in hand)}")
    print()

    if not solution.path:
        print("No playable path found from this open end.")
    else:
        print(f"Path ({len(solution.path)} tiles):  {' '.join(str(d) for d in solution.path)}")
        print(f"  → new open end: {solution.open_end}")

    if solution.remainder:
        print(f"\nRemainder ({len(solution.remainder)} tiles): {' '.join(str(d) for d in solution.remainder)}")
        print("  → dump on Mexican Train or open player trains")
    else:
        print("\nNo tiles left over — full hand fits on personal train!")
