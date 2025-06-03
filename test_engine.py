"""Script used to test an engine's search against results stored a file."""

import os
import re
import sys
import shutil


import board as bd
import constants as cs
import engine_wrapper as ewr


def get_tokens(line):
    """Tokenises a test line string."""
    sections = re.split("(;)", line)
    tokens = []

    for s in sections:
        tokens.extend(s.split(" "))

    return [s.strip() for s in tokens if s and s]


def parse_line(line):
    """Extracts the fen, best move(s) and test id from a line."""
    if not re.match(cs.FEN_REGEX, line):
        return "", [], ""

    tokens = get_tokens(line)

    info = iter(tokens)

    fen = " ".join(tokens[:4])

    hm_clk = 0
    fm_num = 1

    best_moves = []
    test_id_sections = []

    for _ in range(4):
        next(info)

    try:
        tok = next(info)

        if tok.isdigit():
            hm_clk = int(tok)
            tok = next(info)

            if tok.isdigit():
                fm_num = int(tok)
                tok = next(info)

        while True:
            if tok == "bm":
                tok = next(info)
                break
            tok = next(info)

        while True:
            if re.match(cs.MOVE_REGEX_LAN, tok) or re.match(cs.MOVE_REGEX_SAN, tok):
                best_moves.append(tok)
            elif tok in ("id", ";"):
                break
            tok = next(info)

        while tok != "id":
            tok = next(info)
        tok = next(info)

        while tok != ";":
            test_id_sections.append(tok)
            tok = next(info)

    except StopIteration:
        pass

    if not best_moves:
        return "", [], ""

    try:
        hm_clk = int(tokens[tokens.index("hmvc") + 1])
        fm_num = int(tokens[tokens.index("fmvn") + 1])
    except (ValueError, IndexError):
        pass

    fen += f" {hm_clk} {fm_num}"

    test_id = " ".join(test_id_sections)

    return fen, best_moves, test_id


def test_line(e_wrapper, board, line, time):
    """Runs a test from a line in a test file and prints the result."""
    fen, stored_moves, test_id = parse_line(line)

    if not stored_moves:
        return -1

    board.update_board(fen)
    best_moves = []

    for mstr in stored_moves:
        if re.match(cs.MOVE_REGEX_LAN, mstr) is None:
            best_moves.append(board.san_to_lan(mstr))
        else:
            best_moves.append(mstr)

    best_move = e_wrapper.get_best_move(fen=fen, t=time)

    if best_move in best_moves:
        res_str = "PASS"
        result = 1
    else:
        res_str = "FAIL"
        result = 0

    test_id = test_id[:35].replace('"', "")

    print(
        cs.BESTMOVE_FSTRING.format(
            test_id, fen, " ".join(best_moves), best_move, res_str
        )
    )

    return result


def test_file(e_wrapper, file_path, time=10000):
    """Runs tests from an EPD file and prints a table of results."""
    print(
        cs.BESTMOVE_FSTRING.format(
            "ID", "FEN", "Best Move", "Engine's Best Move", "Result"
        )
    )

    total = 0
    passed = 0

    board = bd.Board()

    with open(file_path, "r", encoding="UTF-8") as f:
        lines = f.readlines()
        for line in lines:
            inc = test_line(e_wrapper, board, line, time)
            if inc != -1:
                passed += inc
                total += 1

    print(f"\nTotal: {total}, Passed: {passed}, Failed: {total - passed}")


def main():
    """Starts the engine and runs the engine tests."""
    if len(sys.argv) < 3:
        print("Error: Missing arguments")
        sys.exit(1)

    if shutil.which(sys.argv[1]) is None:
        print("Error: Engine executable not found.")
        sys.exit(1)

    e_wrapper = ewr.EngineWrapper(sys.argv[1])

    if not os.path.isfile(sys.argv[2]):
        print("Error: EPD file not found")
        return

    if len(sys.argv) >= 4 and sys.argv[3].isdigit():
        test_file(e_wrapper, sys.argv[2], time=int(sys.argv[3]))
    else:
        test_file(e_wrapper, sys.argv[2])


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
