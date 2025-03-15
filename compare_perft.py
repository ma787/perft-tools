"""Script used to compare an engine's perft results to Stockfish."""

import re
import shutil
import sys


import pexpect


MOVE_REGEX = r"\A[a-h][1-8][a-h][1-8]([a-z]?)"

FEN_REGEX = (
    r"([pnbrqkPNBRQK1-8]+\/){7}[pnbrqkPNBRQK1-8]+\s[bw]\s([K]?[Q]?[k]?[q]?)"
    r"\s(-|[a-h][36])\s([0-9]+)\s([0-9]+)"
)

STOCKFISH_REGEX = (
    r"(info string(.)*\r\n)+([a-h][1-8][a-h][1-8]([a-z]?): [0-9]+\r\n)+"
    r"\r\nNodes searched: [0-9]+"
)
PERFT_REGEX = r"([a-h][1-8][a-h][1-8]([a-z]?) [0-9]+\r\n)+\r\n[0-9]+"

NAME_REGEX = r"id name (.)*\r\n"

F_STRING = "{:8}{:>16}{:>16}{:>16}"

START_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class EngineWrapper:
    """Class providing methods to run engine and store perft results."""

    def __init__(self, engine_exec):
        self.results = {}
        self.total = 0
        self.proc = pexpect.spawn(f"{engine_exec}")
        self.proc.setecho(False)
        self.proc.sendline("uci")
        self.proc.expect(NAME_REGEX)
        name_list = self.proc.after.decode("UTF-8").split("\r\n")[0].split(" ")
        self.name = " ".join(name_list[2:])

    def clear(self):
        """Clears the currently stored perft results."""
        self.results = {}
        self.total = 0

    def set_position(self, fen, moves=None):
        """Sets the current position that the engine should analyse."""
        if fen == "startpos":
            self.proc.sendline("position startpos")
        elif not moves:
            self.proc.sendline(f"position fen {fen}")
        else:
            self.proc.sendline(f"position fen {fen} moves {" ".join(moves)}")

        self.clear()

    def run(self, depth, reg=PERFT_REGEX):
        """Runs the engine and stores the perft results."""
        self.clear()
        self.proc.sendline(f"go perft {depth}")
        self.proc.expect(reg, timeout=1000)

        lines = list(filter(None, str(self.proc.after.decode("UTF-8")).split("\r\n")))

        for l in lines:
            move_match = re.match(MOVE_REGEX, l)
            if move_match is None:
                continue

            self.results[move_match.group()] = int(
                "".join(filter(str.isdigit, l[move_match.span()[1] :]))
            )

        self.total = int("".join(filter(str.isdigit, lines[-1])))

    def close(self):
        """Ends the engine process."""
        self.proc.close()


class StockFishWrapper(EngineWrapper):
    def __init__(self):
        super().__init__("stockfish")
        self.proc.expect("((.)*\r\n)*")

    def run(self, depth, reg=STOCKFISH_REGEX):
        super().run(depth, reg=reg)

    def get_position(self):
        """Gets the fen string of the engine's current position. Not part of UCI."""
        self.proc.sendline("d")
        self.proc.expect(r"\r\n((.)*\r\n)*Fen: " + FEN_REGEX, timeout=2)

        lines = str(self.proc.after.decode("UTF-8")).split("\r\n")
        return lines[-1].split(": ")[1]


class ComparePerft:
    """Class providing methods to compare the perft output of two engines."""

    def __init__(self, engine_exec):
        self.engine = EngineWrapper(engine_exec)
        self.stockfish = StockFishWrapper()
        self.fen = START_POS
        self.prev_positions = []

        self.stockfish.run(1)
        self.moves = list(self.stockfish.results.keys())

    def set_position(self, fen, moves=None):
        """Updates the current position."""
        self.stockfish.set_position(fen, moves)
        self.engine.set_position(fen, moves)

    def step_back(self):
        """Steps back up the game tree."""
        if len(self.prev_positions) == 0:
            return

        self.fen = self.prev_positions.pop()
        self.stockfish.set_position(self.fen)
        self.engine.set_position(self.fen)

    def step_forward(self, move):
        """Steps forward in the game tree."""
        if not self.moves:
            print("Run diff before trying to step forward")
            return

        if move not in self.moves:
            print("Not a legal move")
            return

        self.stockfish.set_position(self.fen, [move])
        self.engine.set_position(self.fen, [move])

        self.prev_positions.append(self.fen)
        self.fen = self.stockfish.get_position()

    def compare_perft(self, depth):
        """Prints the difference between the engines' perft results at a given depth."""
        print(
            F_STRING.format("Move", self.engine.name, self.stockfish.name, "Difference")
        )

        self.stockfish.run(depth)
        self.engine.run(depth)

        self.moves = list(self.stockfish.results.keys())

        for mstr, e1_res in self.engine.results.items():
            if mstr in self.stockfish.results:
                e2_res = self.stockfish.results.pop(mstr)
                print(F_STRING.format(mstr, e1_res, e2_res, e2_res - e1_res))
            else:
                print(F_STRING.format(mstr, e1_res, "-", -e1_res))

        for mstr, e2_res in self.stockfish.results.items():
            print(F_STRING.format(mstr, "-", e2_res, e2_res))

        print(
            F_STRING.format(
                "Total",
                self.engine.total,
                self.stockfish.total,
                self.stockfish.total - self.engine.total,
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
                    self.set_position("startpos")

            elif args[1] == "fen":
                fen = " ".join(args[2:8])
                moves = []

                if not re.match(FEN_REGEX, fen):
                    return

                if len(args) > 9 and args[8] == "moves":
                    moves = args[9:]

                self.set_position(fen, moves)


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
        user_in = input()
        client.parse_command(user_in)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
