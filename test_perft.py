"""Script used to test engine against perft results stored in a file."""

import datetime
import shutil
import sys
import time

import engine_wrapper as ewr


def parse_results_file(file_path):
    """Extracts perft results from file."""
    stored_results = {}
    max_depth = 0

    with open(file_path, "r", encoding="UTF-8") as f:
        lines = f.readlines()

        for line in lines:
            if line == "/n":
                break

            info = line.split(";")
            fen = info[0].strip()
            stored_results[fen] = {}

            for i in range(1, len(info)):
                result_set = list(filter(None, info[i].split(" ")))
                depth = int(result_set[0].strip()[1:])
                result = int(result_set[1])
                stored_results[fen][depth] = result

                max_depth = max(depth, max_depth)

    return stored_results, max_depth


def run_tests(e_wrapper, stored_results, depth):
    """Runs the stored perft tests and prints the results."""
    n_tests = len(stored_results)

    print(f"{"":12}{"FEN":72}", end="", flush=True)
    for i in range(1, depth + 1):
        print(f"{i:8}", end="", flush=True)
    print(f"{"Time Elapsed":>19}")

    start = time.time()
    n = 1

    for fen, results in stored_results.items():
        print(f"{f"({n}/{n_tests})":12}{fen:72}", end="", flush=True)
        e_wrapper.set_position(fen)

        for i in range(1, depth + 1):
            if i not in results:
                print(f"{'-':>8}", end="", flush=True)
                continue

            e_wrapper.perft(i)
            res = str(e_wrapper.perft_total - results[i])
            print(f"{res:>8}", end="", flush=True)

        elapsed = datetime.timedelta(seconds=time.time() - start)
        print(f"{str(elapsed):>19}")

        n += 1

    end = time.time()
    print(f"\nTime elapsed: {datetime.timedelta(seconds=end - start)}")


def main():
    """Runs the comparison function."""
    if len(sys.argv) < 2:
        print("Error: Missing arguments")
        sys.exit(1)

    if shutil.which(sys.argv[1]) is None:
        print("Error: Engine executable not found.")
        sys.exit(1)

    e_wrapper = ewr.EngineWrapper(sys.argv[1])

    try:
        stored_results, depth = parse_results_file(sys.argv[2])
    except ValueError:
        print("Error: Parse of results file failed.")
        sys.exit(1)

    try:
        depth_arg = int(sys.argv[3])
        if depth_arg > 0:
            depth = depth_arg
    except (IndexError, ValueError):
        pass

    run_tests(e_wrapper, stored_results, depth)
    e_wrapper.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
