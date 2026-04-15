# strategies/random_strat.py
import random
from domino import Domino
from train import Train
from player import Player
from strategies.base import Strategy


class RandomStrategy(Strategy):
    """
    Pick a random legal move every turn.
    No planning, no preference.

    This is our baseline and smoke test — if RandomStrategy can
    complete thousands of games without errors, the game loop is solid.
    """

    def choose_move(
        self,
        player: Player,
        moves: list[tuple[Domino, Train]],
        game,
    ) -> tuple[Domino, Train]:
        return random.choice(moves)