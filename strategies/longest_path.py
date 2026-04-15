# strategies/longest_path.py
from domino import Domino
from train import Train
from player import Player
from strategies.base import Strategy
from solver import solve


class LongestPathStrategy(Strategy):
    """
    Exhaustively finds the longest possible chain through the hand
    starting from the train's current open end.
    Tiebreaks on largest pip sum.
    Replans whenever the path is disrupted.

    Play priority (same as RandomPath but with optimal path):
    1. Doubles NOT on path — prefer other trains to preserve own open end
    2. Non-doubles NOT on path (largest first) — prefer other trains
    3. Next tile on the planned path (own train only)
    """

    def __init__(self):
        self._paths: dict[int, list[Domino]] = {}

    def choose_move(
        self,
        player: Player,
        moves: list[tuple[Domino, Train]],
        game,
    ) -> tuple[Domino, Train]:
        path = self._get_or_build_path(player)

        # Priority 1: doubles not on path
        # Prefer other trains to preserve own train's open_end for the planned path
        off_path_doubles = [
            (d, t) for d, t in moves
            if d.is_double and d not in path
        ]
        if off_path_doubles:
            other = [(d, t) for d, t in off_path_doubles if t.owner != player.index]
            return max(other or off_path_doubles, key=lambda m: m[0].pip_count)

        # Priority 2: non-doubles not on path (largest first)
        # Prefer other trains to preserve own train's open_end for the planned path
        off_path = [
            (d, t) for d, t in moves
            if not d.is_double and d not in path
        ]
        if off_path:
            other = [(d, t) for d, t in off_path if t.owner != player.index]
            return max(other or off_path, key=lambda m: m[0].pip_count)

        # Priority 3: next tile on path — but ONLY on own train
        if path:
            next_tile = path[0]
            path_moves = [
                (d, t) for d, t in moves
                if d == next_tile and t.owner == player.index
            ]
            if path_moves:
                self._paths[player.index] = path[1:]
                return path_moves[0]

        # Fallback
        return max(moves, key=lambda m: m[0].pip_count)

    def _get_or_build_path(self, player: Player) -> list[Domino]:
        path = self._paths.get(player.index, [])
        hand_set = set(player.hand)

        if (path
                and all(d in hand_set for d in path)
                and path[0].matches(player.train.open_end)):
            return path

        solution = solve(player.hand, player.train.open_end)
        self._paths[player.index] = solution.path
        return solution.path
