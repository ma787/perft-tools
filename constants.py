"""Module storing project constants."""

# fmt: off

MOVE_REGEX_LAN = r'[a-h][1-8][a-h][1-8]([nbrq]?)'
MOVE_REGEX_SAN = r'([RNBQKR])?([a-h])?([1-8])?(x)?[a-h][1-8]((=)?[RNBQKR])?(\+|#)?'
CASTLE_MOVE_REGEX = r'(O|0)-(O|0)(-(O|0))?'

FEN_REGEX = (
    r'([pnbrqkPNBRQK1-8]+\/){7}[pnbrqkPNBRQK1-8]+\s[bw]\s(([K]?[Q]?[k]?[q]?)|-)'
    r'\s(-|[a-h][36])'
)

DIFF_FSTRING = "{:8}{:>16}{:>16}{:>16}"

BESTMOVE_FSTRING = "{:<36}{:<72}{:<22}{:<22}{:<6}"

START_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

SQUARES = [
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
]

RANKS = "12345678"
FILES = "abcdefgh"

WHITE = 0
BLACK = 1

KINGSIDE = 0
QUEENSIDE = 1

N, E, S, W = 8, 1, -8, -1

PAWN_STEP = (N, S)
CASTLE_FILES = ("g", "c")
FIRST_RANK = ("1", "8")
FINAL_RANK = ("8", "1")

KNIGHT_VECS = (
    N + N + E, N + N + W, S + S + E, S + S + W,
    N + E + E, N + W + W, S + E + E, S + W + W
)
ROOK_VECS = (N, E, S, W)
BISHOP_VECS = (N + E, N + W, S + E, S + W)
QUEEN_VECS = (N, E, S, W, N + E, N + W, S + E, S + W)

VECS = {
    "N": KNIGHT_VECS,
    "n": KNIGHT_VECS,
    "B": BISHOP_VECS,
    "b": BISHOP_VECS,
    "R": ROOK_VECS,
    "r": ROOK_VECS,
    "Q": QUEEN_VECS,
    "q": QUEEN_VECS,
    "K": QUEEN_VECS,
    "k": QUEEN_VECS
}
