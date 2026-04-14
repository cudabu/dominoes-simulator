# boneyard.py
import random
from domino import Domino


class Boneyard:
    """
    The full set of dominoes for a game. Responsible for:
    - Generating the complete set for a given max pip value
    - Shuffling
    - Dealing hands to players
    - Providing draw functionality during play
    """

    def __init__(self, max_pip: int = 12):
        self.max_pip = max_pip
        self.tiles = self._generate()
        self.shuffle()

    def _generate(self) -> list[Domino]:
        """
        Generate every unique domino in a set.
        For max_pip=6: [0|0], [1|0], [1|1], [2|0], ... [6|6]
        Total tiles = (max_pip + 1) * (max_pip + 2) / 2
        """
        tiles = []
        for high in range(self.max_pip + 1):
            for low in range(high + 1):
                tiles.append(Domino(high, low))
        return tiles

    def shuffle(self):
        random.shuffle(self.tiles)

    def deal(self, num_players: int, tiles_per_player: int) -> list[list[Domino]]:
        """
        Deal hands to players. Removes dealt tiles from the boneyard.

        Returns a list of hands, one per player.
        Raises ValueError if there aren't enough tiles to deal.
        """
        total_needed = num_players * tiles_per_player
        if total_needed > len(self.tiles):
            raise ValueError(
                f"Cannot deal {tiles_per_player} tiles to {num_players} players "
                f"— only {len(self.tiles)} tiles in set."
            )

        hands = []
        for _ in range(num_players):
            hand = self.tiles[:tiles_per_player]
            self.tiles = self.tiles[tiles_per_player:]
            hands.append(hand)

        return hands

    def draw(self) -> Domino | None:
        """
        Draw one tile from the boneyard.
        Returns None if the boneyard is empty.
        """
        if not self.tiles:
            return None
        return self.tiles.pop()

    @property
    def is_empty(self) -> bool:
        return len(self.tiles) == 0

    def __len__(self) -> int:
        return len(self.tiles)

    def __repr__(self) -> str:
        return f"Boneyard({len(self.tiles)} tiles remaining)"


if __name__ == "__main__":

    # Correct tile counts per set size
    # Formula: (n+1)(n+2)/2
    for max_pip, expected in [(6, 28), (9, 55), (12, 91)]:
        b = Boneyard(max_pip)
        assert len(b) == expected, f"Expected {expected} tiles for double-{max_pip}, got {len(b)}"
        print(f"Double-{max_pip} set: {len(b)} tiles ✓")

    # Every tile is unique
    b = Boneyard(12)
    tile_set = set(b.tiles)
    assert len(tile_set) == len(b.tiles), "Duplicate tiles found!"
    print("All tiles unique ✓")

    # No tile exceeds max_pip
    assert all(d.high <= b.max_pip for d in b.tiles)
    print("No tile exceeds max pip ✓")

    # Dealing reduces boneyard correctly
    b = Boneyard(12)
    hands = b.deal(num_players=4, tiles_per_player=15)
    assert len(hands) == 4
    assert all(len(h) == 15 for h in hands)
    assert len(b) == 91 - 60, f"Expected 31 tiles remaining, got {len(b)}"
    print(f"Deal 4x15 from double-12: {len(b)} tiles remaining ✓")

    # All dealt tiles are unique across all hands
    all_dealt = [tile for hand in hands for tile in hand]
    assert len(set(all_dealt)) == len(all_dealt), "Duplicate tiles dealt!"
    print("No duplicates across hands ✓")

    # Drawing reduces boneyard
    tile = b.draw()
    assert tile is not None
    assert len(b) == 30
    print(f"Draw one tile: {tile}, {len(b)} remaining ✓")

    # Draw until empty
    while not b.is_empty:
        b.draw()
    assert b.draw() is None
    print("Draw from empty boneyard returns None ✓")

    # Can't deal more than available
    b = Boneyard(6)
    try:
        b.deal(num_players=4, tiles_per_player=20)
        assert False, "Should have raised"
    except ValueError:
        print("Overdeal raises ValueError ✓")

    print("\nAll checks passed.")
    print("\nDealing a test hand:")

    b = Boneyard(12)
    hands = b.deal(4, 15)
    for i, hand in enumerate(hands):
        print(f"Player {i}: {hand}")