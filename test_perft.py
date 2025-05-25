"""Script used to test engine against perft results stored in a file."""

import datetime
import shutil
import sys
import time

import pexpect

import constants as cs


def parse_results_file(file_path):
    """Extracts perft results from file."""
    all_results = {}

    with open(file_path, "r", encoding="UTF-8") as f:
        lines = f.readlines()

        for line in lines:
            if line == "/n":
                break

            info = line.split(";")
            fen = info[0].strip()
            all_results[fen] = {}

            for i in range(1, len(info)):
                result = info[i].split(" ")
                all_results[fen][int(result[0][1:])] = int(result[1])

    return all_results


def main():
    """Runs the comparison function."""
    if len(sys.argv) < 2:
        print("Error: Missing arguments")
        sys.exit(1)

    if shutil.which(sys.argv[1]) is None:
        print("Error: Engine executable not found.")
        sys.exit(1)

    try:
        all_tests = parse_results_file(sys.argv[2])
        n_tests = len(all_tests)
    except ValueError:
        print("Error: Parse of results file failed.")
        sys.exit(1)

    try:
        depth = int(sys.argv[3])
        if depth < 0:
            depth = 6
    except ValueError:
        depth = 6

    proc = pexpect.spawn(sys.argv[1])
    proc.setecho(False)
    proc.sendline("uci")

    proc.expect(cs.NAME_REGEX)
    name_list = proc.after.decode("UTF-8").split("\r\n")[0].split(" ")
    name = " ".join(name_list[2:])

    if "stockfish" in name.lower():
        reg = cs.STOCKFISH_REGEX
    else:
        reg = cs.PERFT_REGEX

    print(f"{"":12}{"FEN":72}", end="", flush=True)
    for i in range(1, depth + 1):
        print(f"{i:8}", end="", flush=True)
    print(f"{"Time Elapsed":>19}")

    start = time.time()
    n = 1

    for fen, results in all_tests.items():
        print(f"{f"({n}/{n_tests})":12}{fen:72}", end="", flush=True)

        proc.sendline(f"position fen {fen}")
        proc.expect("")

        for i in range(1, depth + 1):
            if i not in results:
                print(f"{'-':>8}", end="", flush=True)
                continue

            proc.sendline(f"go perft {i}")
            proc.expect(reg, timeout=None)

            lines = list(filter(None, proc.after.decode("UTF-8").split("\r\n")))
            perft_result = int("".join(filter(str.isdigit, lines[-1])))
            res = str(perft_result - results[i])

            print(f"{res:>8}", end="", flush=True)

        elapsed = datetime.timedelta(seconds=time.time() - start)
        print(f"{str(elapsed):>19}")

        n += 1

    end = time.time()
    print(f"\nTime elapsed: {datetime.timedelta(seconds=end - start)}")
    proc.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
