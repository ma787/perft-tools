import os
import re
import sys
import shutil


import engine_wrapper as ewr
import constants as cs


class EngineMoveTester(ewr.EngineWrapper):
    def __init__(self, engine_exec):
        super().__init__(engine_exec)
        self.board = ["-" for _ in range(64)]
        self.fen = ""
        self.parse_fen(cs.START_POS)
        self.side = cs.WHITE
        self.best_moves = []
        self.id = ""

    @staticmethod
    def flip(i):
        """Vertically flips a board coordinate."""
        return i ^ 56

    def parse_fen(self, fen_str):
        """Fills a board array of strings by parsing a fen string."""
        for i in range(64):
            self.board[i] = "-"

        i = 0
        b_index = 0
        char = fen_str[i]

        while char != " ":
            if char.isdigit():
                for j in range(int(char)):
                    self.board[EngineMoveTester.flip(b_index + j)] = "-"
                b_index += int(char)
            elif char != "/":
                self.board[EngineMoveTester.flip(b_index)] = char
                b_index += 1

            i += 1
            char = fen_str[i]

        i += 1
        self.side = cs.WHITE if fen_str[i] == "w" else cs.BLACK
        self.fen = fen_str[: i + 5] + " 0 1"

        return i + 9  # skip to best move string

    def parse_line(self, line):
        """Updates the board position and retrieves best moves from a line."""
        if not re.match(cs.FEN_REGEX_SHORT, line):
            return

        i = self.parse_fen(line)
        self.best_moves = []
        char = ""

        while True:
            char = line[i]

            if char == ";":
                break

            if char == " ":
                i += 1
                continue

            san_match = re.match(cs.MOVE_REGEX_SAN, line[i:])
            if san_match:
                self.best_moves.append(self.san_to_lan(san_match.group()))
                i += san_match.span()[1]
            else:
                self.best_moves.append(line[i : i + 4])
                i += 4

        i += 5
        id_match = re.match(r'"(.*?)"', line[i:])
        self.id = id_match.group()[1:-1]

    def get_possible_squares(self, p_type, dest, squares):
        """Populates an array with all possible start squares of a move."""
        if self.side == cs.BLACK:
            p_type = p_type.lower()

        if p_type.lower() not in ("b", "r", "q"):
            for v in cs.VECS[p_type]:
                try:
                    sq = cs.SQUARES[dest + v]
                    if self.board[dest + v] == p_type:
                        squares.append(sq)
                except IndexError:
                    continue
            return

        for v in cs.VECS[p_type]:
            i = dest + v
            while 0 <= i <= 63:
                sq = cs.SQUARES[i]

                if self.board[i] == p_type:
                    squares.append(sq)
                elif self.board[i] != "-":
                    break

                i += v

    def san_to_lan(self, mstr):
        """Returns a move string in LAN."""
        if re.match(cs.CASTLE_REGEX, mstr):
            c_type = cs.KINGSIDE if len(mstr) == 3 else cs.QUEENSIDE
            start_str = "e" + cs.FIRST_RANK[self.side]
            dest_str = cs.CASTLE_FILES[c_type] + cs.FIRST_RANK[self.side]
            return start_str + dest_str

        if mstr[-1] in ("+", "#"):
            mstr = mstr[:-1]

        if mstr[-2] == "=":
            mstr = mstr[:-2]

        dest_str = mstr[-2:]
        dest = cs.SQUARES.index(dest_str)
        pawn_step = cs.PAWN_STEP[self.side]

        if len(mstr) == 2:
            if self.board[dest - pawn_step] != "-":
                return cs.SQUARES[dest - pawn_step] + dest_str

            return cs.SQUARES[dest - (2 * pawn_step)] + dest_str

        if mstr[0] in cs.FILES and mstr[1] == "x":
            return mstr[0] + cs.SQUARES[dest - pawn_step][1] + dest_str

        p_type = mstr[0]
        start_squares = []
        self.get_possible_squares(p_type, dest, start_squares)

        if len(start_squares) == 1:
            return start_squares[0] + dest_str

        if mstr[1:3] in cs.SQUARES:
            return mstr[1:3] + dest_str

        if mstr[1] in cs.FILES:
            start_str = [x for x in start_squares if x[0] == mstr[1]][0]
        elif mstr[1] in cs.RANKS:
            start_str = [x for x in start_squares if x[1] == mstr[1]][0]
        else:
            raise ValueError

        return start_str + dest_str

    def test_line(self, line, time):
        """Runs a test from a line in a test file and prints the result."""
        self.parse_line(line)
        self.set_position(self.fen)
        self.proc.sendline(f"go movetime {time}")
        self.proc.expect(cs.BESTMOVE_REGEX, timeout=1000)

        lines = list(filter(None, str(self.proc.after.decode("UTF-8")).split("\r\n")))
        best_move_str = lines[-1][-4:]

        if best_move_str in self.best_moves:
            res_str = "PASS"
            result = 1
        else:
            res_str = "FAIL"
            result = 0

        print(
            cs.BESTMOVE_FSTRING.format(
                self.id, self.fen, self.best_moves[0], best_move_str, res_str
            )
        )

        return result

    def test_file(self, file_path, time=10000):
        """Runs tests from an EPD file and prints a table of results."""
        print(
            cs.BESTMOVE_FSTRING.format(
                "ID", "FEN", "Best Move", "Engine's Best Move", "Result"
            )
        )

        total = 0
        passed = 0

        with open(file_path, "r", encoding="UTF-8") as f:
            lines = f.readlines()
            for line in lines:
                passed += self.test_line(line, time)
                total += 1

        print(f"\nTotal: {total}, Passed: {passed}, Failed: {total - passed}")


def main():
    if len(sys.argv) < 3:
        print("Error: Missing arguments")
        sys.exit(1)

    if shutil.which(sys.argv[1]) is None:
        print("Error: Engine executable not found.")
        sys.exit(1)

    e_tester = EngineMoveTester(sys.argv[1])

    if not os.path.isfile(sys.argv[2]):
        print("Error: EPD file not found")

    if len(sys.argv) >= 4 and sys.argv[3].isdigit():
        e_tester.test_file(sys.argv[2], time=int(sys.argv[3]))
    else:
        e_tester.test_file(sys.argv[2])


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
