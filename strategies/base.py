# strategies/base.py
from abc import ABC, abstractmethod
from domino import Domino
from train import Train
from player import Player


class Strategy(ABC):

    @abstractmethod
    def choose_move(
        self,
        player: Player,
        moves: list[tuple[Domino, Train]],
        game,
    ) -> tuple[Domino, Train]:
        
        """
        Given a player and their legal moves, return the chosen (domino, train).

        player: the player whose turn it is
        moves:  list of (domino, train) pairs — all are legal, never empty
        game:   the Game instance — read only, for context if needed
        """
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__