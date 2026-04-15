# game.py
from boneyard import Boneyard
from domino import Domino
from player import Player
from train import Train


# Tiles per player by (max_pip, num_players).
# Official recommendations:
#   D9:  2-3 players  → 8 tiles
#   D12: 4-6 players  → 12 tiles, 7-8 players → 10 tiles
#   D15: 9-12 players → 11 tiles
#   D18: 13-14 players → 11 tiles
# Non-recommended combinations use derived values.
HAND_SIZES = {
    6:  {2: 7,  3: 7,  4: 6},
    9:  {2: 8,  3: 8,  4: 10, 5: 9,  6: 8},
    12: {2: 15, 3: 15, 4: 12, 5: 12, 6: 12, 7: 10, 8: 10, 9: 9,  10: 8,  11: 7,  12: 7,  13: 6,  14: 6},
    15: {2: 20, 3: 18, 4: 15, 5: 14, 6: 13, 7: 12, 8: 11, 9: 11, 10: 11, 11: 11, 12: 11, 13: 10, 14: 9},
    18: {2: 25, 3: 22, 4: 20, 5: 18, 6: 17, 7: 16, 8: 14, 9: 13, 10: 12, 11: 12, 12: 11, 13: 11, 14: 11},
}


class Game:
    """
    Manages a full game of Mexican Train across all rounds.

    One round per double in the set (max_pip+1 rounds total).
    Each round uses a different engine double, descending from max_pip to 0.

    Responsibilities:
    - Round setup and teardown
    - Turn rotation
    - Legal move calculation (respecting double satisfaction)
    - Executing moves and updating state
    - Detecting round end conditions
    - Scoring
    """

    def __init__(self, players: list[Player], max_pip: int = 12):
        self.players = players
        self.max_pip = max_pip
        self.num_players = len(players)
        self.mexican_train: Train | None = None
        self.boneyard: Boneyard | None = None
        self.unsatisfied_double: int | None = None  # pip value of exposed double
        self.current_round: int = 0                 # tracks which engine double we're on
        self.round_log: list[str] = []              # human-readable turn log

    # ------------------------------------------------------------------
    # Round management
    # ------------------------------------------------------------------

    def setup_round(self, engine_pip: int):
        """
        Prepare all state for a new round.
        Deals hands, resets trains, clears boneyard.
        """
        self.current_round = engine_pip
        self.unsatisfied_double = None
        #self.round_log = []

        # Fresh boneyard, remove the engine double first
        self.boneyard = Boneyard(max_pip=self.max_pip)
        engine = Domino(engine_pip, engine_pip)
        self.boneyard.tiles.remove(engine)

        # Deal hands
        num_players = len(self.players)
        tiles_per_player = HAND_SIZES[self.max_pip].get(num_players, 10)
        hands = self.boneyard.deal(num_players, tiles_per_player)

        # Reset each player
        for i, player in enumerate(self.players):
            player.reset_for_round(hands[i], engine_pip)

        # Fresh Mexican Train
        self.mexican_train = Train(owner=None, engine_pip=engine_pip)

        self._log(f"\n{'='*40}")
        self._log(f"--- Round engine: [{engine_pip}|{engine_pip}] ---")

    def end_round(self):
        self._log("--- Round over ---")
        for player in self.players:
            pips_this_round = player.hand_pip_count  # capture BEFORE end_round clears it
            player.end_round()
            self._log(f"Player {player.index}: +{pips_this_round} pips | Total: {player.score}")

    # ------------------------------------------------------------------
    # Turn logic
    # ------------------------------------------------------------------

    def visible_trains(self, player: Player) -> list[Train]:
        """
        Returns all trains this player can legally play on:
        - Their own train (always)
        - Any other player's train that is open
        - The Mexican Train (always open)
        """
        trains = [player.train]
        for other in self.players:
            if other.index != player.index and other.train.is_open:
                trains.append(other.train)
        trains.append(self.mexican_train)
        return trains

    def legal_moves(self, player: Player) -> list[tuple[Domino, Train]]:
        trains = self.visible_trains(player)

        if self.unsatisfied_double is not None:
            # Only tiles matching the unsatisfied double pip value
            # on ANY visible train that can accept them
            return [
                (domino, train)
                for domino, train in player.playable_tiles(trains)
                if domino.matches(self.unsatisfied_double)
            ]

        return player.playable_tiles(trains)

    def execute_move(self, player: Player, domino: Domino, train: Train):
        """
        Apply a move: remove tile from hand, play onto train,
        update double satisfaction state, close train if appropriate.
        """
        player.remove(domino)
        train.play(domino)

        # If a double was just played, it needs to be satisfied
        if domino.is_double:
            self.unsatisfied_double = domino.high
            self._log(f"  Player {player.index} played {domino} (double — must satisfy!)")
        else:
            # Tile played — if it matches an unsatisfied double it satisfies it
            if self.unsatisfied_double is not None:
                self.unsatisfied_double = None
                self._log(f"  Player {player.index} satisfied the double with {domino}")
            else:
                self._log(f"  Player {player.index} played {domino} on {self._train_label(train)}")

        # Close the player's own train if they just played on it
        if train.owner == player.index:
            train.close()

    def take_turn(self, player: Player, strategy) -> tuple[bool, bool]:
        """
        Returns (went_out, did_pass)
        """
        moves = self.legal_moves(player)

        if not moves:
            drawn = player.draw(self.boneyard)
            if drawn is not None:
                self._log(f"  Player {player.index} draws {drawn}")
                moves = self.legal_moves(player)

        if not moves:
            player.train.open()
            self._log(f"  Player {player.index} passes (train opened)")
            return False, True  # did not go out, did pass

        domino, train = strategy.choose_move(player, moves, self)
        self.execute_move(player, domino, train)

        if player.hand_is_empty:
            self._log(f"  Player {player.index} is out!")
            return True, False  # went out, did not pass

        return False, False  # neither

    # ------------------------------------------------------------------
    # Round loop
    # ------------------------------------------------------------------

    def play_round(self, strategies: list) -> int | None:
        consecutive_passes = 0

        while True:
            for i, player in enumerate(self.players):
                if player.is_out:
                    continue

                went_out, did_pass = self.take_turn(player, strategies[i])

                if went_out:
                    return player.index

                if did_pass:
                    consecutive_passes += 1
                else:
                    consecutive_passes = 0

                if consecutive_passes >= self.num_players:
                    self._log("Stalemate — no player can move.")
                    return None


    # ------------------------------------------------------------------
    # Full game
    # ------------------------------------------------------------------

    def play_game(self, strategies: list) -> list[int]:
        """
        Play a full game (one round per double, descending).
        Returns final scores for each player.
        """
        for engine_pip in range(self.max_pip, -1, -1):
            self.setup_round(engine_pip)
            self.play_round(strategies)
            self.end_round()

        return [p.score for p in self.players]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _train_label(self, train: Train) -> str:
        if train.is_mexican_train:
            return "Mexican Train"
        return f"Player {train.owner}'s train"

    def _log(self, message: str):
        self.round_log.append(message)

    def print_log(self):
        for line in self.round_log:
            print(line)

    def print_scores(self):
        print("\nCurrent scores:")
        for player in sorted(self.players, key=lambda p: p.score):
            print(f"  Player {player.index}: {player.score}")


if __name__ == "__main__":
    import random as rng
    from boneyard import Boneyard

    # Throwaway random strategy just for smoke testing
    class _RandomStrategy:
        def choose_move(self, player, moves, game):
            return rng.choice(moves)

    # Build 4 players (hands assigned during setup_round)
    players = [Player(i, [], engine_pip=12) for i in range(4)]
    game = Game(players, max_pip=12)
    strategies = [_RandomStrategy() for _ in range(4)]

    # Play one round
    game.setup_round(engine_pip=12)
    result = game.play_round(strategies)
    game.end_round()

    game.print_log()
    game.print_scores()

    print(f"\nRound winner: Player {result}" if result is not None else "\nRound ended in stalemate")
    print("\nSmoke test passed ✓")