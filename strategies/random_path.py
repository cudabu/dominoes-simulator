# strategies/random_path.py
import random
from domino import Domino
from train import Train
from player import Player
from strategies.base import Strategy


class RandomPathStrategy(Strategy):
    """
    Builds a path through the hand by randomly extending a chain
    from the current train end. Replans whenever the path is disrupted.

    Play priority
    1. Doubles that are NOT on the path — get rid of them
    2. Non-double tiles NOT on the path — shed off-path weight
    3. The next tile on the planned path

    Path is stored on the strategy instance per player index so it
    persists across turns but can be rebuilt when disrupted.
    """

    def __init__(self):
        # Keyed by player index so we can handle multiple players
        # using this same strategy class in one game
        self._paths: dict[int, list[Domino]] = {}

    def choose_move(
        self,
        player: Player,
        moves: list[tuple[Domino, Train]],
        game,
    ) -> tuple[Domino, Train]:
        # Rebuild path if we don't have one or it's been disrupted
        path = self._get_or_build_path(player)

        # Priority 1: play a double that is NOT on the path
        # Prefer other trains to preserve own train's open_end for the planned path
        off_path_doubles = [
            (d, t) for d, t in moves
            if d.is_double and d not in path
        ]
        if off_path_doubles:
            other = [(d, t) for d, t in off_path_doubles if t.owner != player.index]
            return random.choice(other or off_path_doubles)

        # Priority 2: play a non-double NOT on the path (largest first)
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
                if d == next_tile and t.owner == player.index  # must be own train
            ]
            if path_moves:
                self._paths[player.index] = path[1:]
                return path_moves[0]

        # Fallback: any legal move
        return random.choice(moves)


    def _get_or_build_path(self, player: Player) -> list[Domino]:
        path = self._paths.get(player.index, [])
        hand_set = set(player.hand)

        if (path
                and all(d in hand_set for d in path)
                and path[0].matches(player.train.open_end)):
            return path

        path = self._build_random_path(player)
        self._paths[player.index] = path
        return path


    def _build_random_path(self, player: Player) -> list[Domino]:
        """
        Build a path by randomly extending from the train's open end.
        Keeps picking a random matching tile until no extension is possible.
        """
        open_end = player.train.open_end
        remaining = list(player.hand)
        path = []

        while True:
            # Find all tiles in remaining hand that match the open end
            candidates = [d for d in remaining if d.matches(open_end)]
            if not candidates:
                break

            chosen = random.choice(candidates)
            path.append(chosen)
            remaining.remove(chosen)
            open_end = chosen.other_end(open_end)

        return path