"""Script used to compare an engine's perft results to Stockfish."""

import re
import shutil
import sys


import engine_wrapper as ewr
import constants as cs


class ComparePerft:
    """Class providing methods to compare the perft output of two engines."""

    def __init__(self, engine_exec):
        self.engine = ewr.EngineWrapper(engine_exec)
        self.stockfish = ewr.EngineWrapper("stockfish")
        self.fen = cs.START_POS
        self.move_history = []
        self.legal_moves = []

    def update_position(self, fen, moves=None):
        """Updates the current position."""
        if fen == "startpos":
            fen = cs.START_POS

        self.stockfish.set_position(fen, moves)
        self.engine.set_position(fen, moves)
        self.fen = fen
        self.move_history = []
        self.legal_moves = []

    def step_back(self):
        """Steps back up the game tree."""
        if len(self.move_history) == 0:
            return

        self.move_history.pop()
        self.stockfish.set_position(self.fen, self.move_history)
        self.engine.set_position(self.fen, self.move_history)

    def step_forward(self, move):
        """Steps forward in the game tree."""
        if not self.legal_moves:
            print("Run diff before trying to step forward")
            return

        if move not in self.legal_moves:
            print("Not a legal move")
            return

        self.move_history.append(move)
        self.stockfish.set_position(self.fen, self.move_history)
        self.engine.set_position(self.fen, self.move_history)

    def compare_perft(self, depth):
        """Prints the difference between the engines' perft results at a given depth."""
        print(
            cs.DIFF_FSTRING.format(
                "Move", self.engine.name, self.stockfish.name, "Difference"
            )
        )

        self.stockfish.perft(depth)
        self.engine.perft(depth)

        self.legal_moves = list(self.stockfish.perft_results.keys())

        for mstr, e1_res in self.engine.perft_results.items():
            if mstr in self.stockfish.perft_results:
                e2_res = self.stockfish.perft_results.pop(mstr)
                print(cs.DIFF_FSTRING.format(mstr, e1_res, e2_res, e2_res - e1_res))
            else:
                print(cs.DIFF_FSTRING.format(mstr, e1_res, "-", -e1_res))

        for mstr, e2_res in self.stockfish.perft_results.items():
            print(cs.DIFF_FSTRING.format(mstr, "-", e2_res, e2_res))

        print(
            cs.DIFF_FSTRING.format(
                "Total",
                self.engine.perft_total,
                self.stockfish.perft_total,
                self.stockfish.perft_total - self.engine.perft_total,
            )
        )

    def parse_command(self, cmd):
        """Parses a user input."""
        args = cmd.split(" ")

        if cmd == "quit":
            self.engine.close()
            self.stockfish.close()
            sys.exit()

        if cmd in ("b", "back"):
            self.step_back()

        elif re.match(r"diff [0-9]+", cmd):
            self.compare_perft(int(args[1]))

        elif re.match(r"move (.)+", cmd):
            self.step_forward(args[1])

        elif re.match(r"position", cmd):
            if len(args) < 8:
                if len(args) == 2 and args[1] == "startpos":
                    self.update_position("startpos")

            elif args[1] == "fen":
                fen = " ".join(args[2:8])
                moves = []

                if not re.match(cs.FEN_REGEX, fen):
                    return

                if len(args) > 9 and args[8] == "moves":
                    moves = args[9:]

                self.update_position(fen, moves)


def main():
    """Runs the engines and prints the difference in perft results."""
    if len(sys.argv) < 2:
        print("Engine executable not provided")
        sys.exit()

    if not shutil.which(sys.argv[1]):
        print("Engine executable not found")
        sys.exit()

    client = ComparePerft(sys.argv[1])

    while True:
        client.parse_command(input())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
