# strategies/greedy.py
from domino import Domino
from train import Train
from player import Player
from strategies.base import Strategy


class GreedyStrategy(Strategy):
    """
    Always play the legal move with the highest pip count.
    No path planning — just shed as many pips as possible right now.

    Noticeably smarter than Random but still short-sighted.
    It doesn't consider whether playing a tile blocks future plays.
    """

    def choose_move(
        self,
        player: Player,
        moves: list[tuple[Domino, Train]],
        game,
    ) -> tuple[Domino, Train]:
        return max(moves, key=lambda move: move[0].pip_count)