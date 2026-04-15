# player.py
from domino import Domino
from train import Train


class Player:
    """
    Represents a single player in the game.

    A player has:
    - An index (0, 1, 2...) used to identify them
    - A hand of dominoes
    - A personal train
    - A cumulative score across rounds

    Player holds state only. Strategy logic lives in strategies/.
    That separation means we can plug any strategy into any player
    without changing this file.
    """

    def __init__(self, index: int, hand: list[Domino], engine_pip: int):
        """
        index:      Player's position at the table (0-based)
        hand:       Tiles dealt from the boneyard
        engine_pip: The starting pip for this round's personal train
        """
        self.index = index
        self.hand = hand
        self.train = Train(owner=index, engine_pip=engine_pip)
        self.score = 0              # cumulative across rounds
        self.is_out = False         # True when hand is empty

    # ------------------------------------------------------------------
    # Hand inspection
    # ------------------------------------------------------------------

    @property
    def hand_pip_count(self) -> int:
        """Total pips remaining in hand. This is added to score if round ends."""
        return sum(d.pip_count for d in self.hand)

    @property
    def hand_is_empty(self) -> bool:
        return len(self.hand) == 0

    def has_playable(self, trains: list[Train]) -> bool:
        """
        Returns True if any tile in hand can be played on any visible train.
        'Visible' means: open trains + this player's own train.
        """
        for domino in self.hand:
            for train in trains:
                if train.can_play(domino):
                    return True
        return False

    def playable_tiles(self, trains: list[Train]) -> list[tuple[Domino, Train]]:
        """
        Returns all legal (domino, train) pairs this player can play.
        Used by strategies to evaluate options.
        """
        moves = []
        for domino in self.hand:
            for train in trains:
                if train.can_play(domino):
                    moves.append((domino, train))
        return moves

    # ------------------------------------------------------------------
    # Mutating state
    # ------------------------------------------------------------------

    def remove(self, domino: Domino):
        """
        Remove a domino from hand after playing it.
        Raises ValueError if the domino isn't in hand.
        """
        try:
            self.hand.remove(domino)
        except ValueError:
            raise ValueError(f"{domino} is not in Player {self.index}'s hand.")

        if self.hand_is_empty:
            self.is_out = True

    def draw(self, boneyard) -> Domino | None:
        """
        Draw one tile from the boneyard and add it to hand.
        Returns the drawn tile, or None if boneyard is empty.
        """
        tile = boneyard.draw()
        if tile is not None:
            self.hand.append(tile)
        return tile

    def end_round(self):
        """
        Called at the end of a round.
        Adds remaining hand pips to cumulative score and resets hand state.
        Score accumulates — it is NOT reset between rounds.
        """
        self.score += self.hand_pip_count

    def reset_for_round(self, hand: list[Domino], engine_pip: int):
        """
        Prepare this player for a new round with a fresh hand and train.
        Score is preserved — only hand and train reset.
        """
        self.hand = hand
        self.train = Train(owner=self.index, engine_pip=engine_pip)
        self.is_out = False

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Player {self.index} | "
            f"Hand: {self.hand} | "
            f"Pips: {self.hand_pip_count} | "
            f"Score: {self.score}"
        )


if __name__ == "__main__":
    from boneyard import Boneyard

    # Deal a real hand from a boneyard
    b = Boneyard(max_pip=12)
    hands = b.deal(num_players=2, tiles_per_player=15)

    p0 = Player(index=0, hand=hands[0], engine_pip=12)
    p1 = Player(index=1, hand=hands[1], engine_pip=12)

    print(f"Setup:         {p0}")
    print(f"               {p1}")

    # hand_pip_count
    assert p0.hand_pip_count == sum(d.pip_count for d in p0.hand)
    print(f"Pip count:     Player 0 has {p0.hand_pip_count} pips ✓")

    # has_playable — check against own train (open end is 12)
    trains = [p0.train]
    playable = p0.has_playable(trains)
    print(f"has_playable:  {playable} (depends on hand, both outcomes valid) ✓")

    # playable_tiles returns (domino, train) pairs
    moves = p0.playable_tiles(trains)
    print(f"playable_tiles: {len(moves)} legal moves against own train ✓")

    # remove a tile from hand
    tile_to_remove = p0.hand[0]
    original_count = len(p0.hand)
    p0.remove(tile_to_remove)
    assert len(p0.hand) == original_count - 1
    assert tile_to_remove not in p0.hand
    print(f"remove:        {tile_to_remove} removed from hand ✓")

    # removing a tile not in hand raises
    try:
        p0.remove(Domino(0, 0))
        assert False, "Should have raised"
    except ValueError:
        print("Bad remove:    raises ValueError ✓")

    # draw from boneyard
    hand_size = len(p0.hand)
    drawn = p0.draw(b)
    assert len(p0.hand) == hand_size + 1
    print(f"draw:          drew {drawn}, hand now {len(p0.hand)} tiles ✓")

    # end_round accumulates score
    pips_before = p0.hand_pip_count
    p0.end_round()
    assert p0.score == pips_before
    print(f"end_round:     score is now {p0.score} ✓")

    # reset_for_round preserves score, resets hand and train
    score_before = p0.score
    new_hands = b.deal(num_players=1, tiles_per_player=15)
    p0.reset_for_round(hand=new_hands[0], engine_pip=11)
    assert p0.score == score_before
    assert p0.train.engine_pip == 11
    assert not p0.is_out
    print(f"reset_for_round: score preserved ({p0.score}), new train at pip 11 ✓")

    # is_out triggers when hand emptied
    p_small = Player(index=2, hand=[Domino(3, 2)], engine_pip=12)
    assert not p_small.is_out
    p_small.remove(Domino(3, 2))
    assert p_small.is_out
    print("is_out:        triggers on empty hand ✓")

    print("\nAll checks passed.")

    print("\nPlay real game.")

    b = Boneyard(12)
    hands = b.deal(4, 15)
    players = [Player(i, hands[i], engine_pip=12) for i in range(4)]

    for p in players:
        print(p)