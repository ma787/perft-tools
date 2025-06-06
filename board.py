import re


import constants as cs


class Board:
    """A class that stores some aspects of a chess position."""

    def __init__(self):
        self.board = ["-" for _ in range(64)]
        self.side = cs.WHITE
        self.update_board(cs.START_POS)

    @staticmethod
    def flip(pos):
        """Vertically flips a board coordinate."""
        return pos ^ 56

    def update_board(self, board_string):
        """Fills a board array by parsing a fen string."""
        for i in range(64):
            self.board[i] = "-"

        i = 0
        b_index = 0
        char = board_string[i]

        while char != " ":
            if char.isdigit():
                for j in range(int(char)):
                    self.board[Board.flip(b_index + j)] = "-"
                b_index += int(char)
            elif char != "/":
                self.board[Board.flip(b_index)] = char
                b_index += 1

            i += 1
            char = board_string[i]

        self.side = cs.WHITE if board_string[i + 1] == "w" else cs.BLACK

    def make_move(self, mstr):
        """Updates the board representation with a move."""
        start = cs.SQUARES.index(mstr[:2])
        dest = cs.SQUARES.index(mstr[2:4])
        piece = self.board[start]

        self.board[start] = "-"
        self.board[dest] = piece

        if piece.lower() == "p":
            vec = dest - start

            # en passant
            if vec != cs.PAWN_STEP[self.side] and self.board[dest] == "-":
                self.board[dest - cs.PAWN_STEP[self.side]] = "-"

            # promotion
            if mstr[3] == cs.FINAL_RANK[self.side]:
                assert (len(mstr)) == 5
                self.board[dest] = mstr[-1]

                if self.side == cs.WHITE:
                    self.board[dest] = mstr[-1].upper()

        if piece.lower() == "k" and mstr[0] == "e":
            rook = "R" if self.side == cs.WHITE else "r"

            if mstr[2] == "c":  # queenside castle
                self.board[cs.SQUARES.index("a" + cs.FIRST_RANK[self.side])] = "-"
                self.board[cs.SQUARES.index("d" + cs.FIRST_RANK[self.side])] = rook
            elif mstr[2] == "g":  # kingside castle
                self.board[cs.SQUARES.index("h" + cs.FIRST_RANK[self.side])] = "-"
                self.board[cs.SQUARES.index("f" + cs.FIRST_RANK[self.side])] = rook

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
                    break

                if self.board[i] != "-":
                    break

                i += v

    def san_to_lan(self, mstr):
        """Returns a move string in LAN."""
        if re.match(cs.CASTLE_MOVE_REGEX, mstr):
            c_type = cs.KINGSIDE if len(mstr) == 3 else cs.QUEENSIDE
            start_str = "e" + cs.FIRST_RANK[self.side]
            dest_str = cs.CASTLE_FILES[c_type] + cs.FIRST_RANK[self.side]
            return start_str + dest_str

        pr_type = ""

        if mstr[-1] in ("+", "#"):
            mstr = mstr[:-1]

        if mstr[-1].lower() in ("n", "b", "r", "q"):
            pr_type = mstr[-1].lower()
            mstr = mstr[:-1]
            if mstr[-1] == "=":
                mstr = mstr[:-1]

        dest_str = mstr[-2:]
        dest = cs.SQUARES.index(dest_str)
        pawn_step = cs.PAWN_STEP[self.side]

        if len(mstr) == 2:
            if self.board[dest - pawn_step] != "-":
                start_str = cs.SQUARES[dest - pawn_step]
            else:
                start_str = cs.SQUARES[dest - (2 * pawn_step)]

            return start_str + dest_str + pr_type

        if mstr[0] in cs.FILES and mstr[1] == "x":
            return mstr[0] + cs.SQUARES[dest - pawn_step][1] + dest_str + pr_type

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
