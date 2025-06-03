"""Module providing functions to communicate with a UCI engine."""

import re
import subprocess
import time

import constants as cs


class EngineWrapper:
    """Class providing methods to control the engine process."""

    def __init__(self, engine_exec):
        self.exec_name = engine_exec
        self.name = self.get_name()

    def get_name(self):
        """Gets the name of the engine, if it is reported."""
        with subprocess.Popen(
            [self.exec_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        ) as proc:
            output = proc.communicate("uci\nquit")[0]
            for l in output.split("\n"):
                if re.match(r"id name", l):
                    return " ".join(l.split(" ")[2:])

        return ""

    def perft(self, depth, fen=cs.START_POS, moves=None):
        """Runs the perft command and returns the result."""
        if depth < 1:
            return {}, 0

        command = f"position fen {fen}"

        if moves:
            command += " moves " + " ".join(moves)

        command += f"\ngo perft {depth}\nquit"

        with subprocess.Popen(
            [self.exec_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        ) as proc:
            output = proc.communicate(command)[0]
            lines = output.split("\n")

            tokens = []
            for l in lines:
                tokens.extend(l.split())

            i = 0
            while True:
                tok = tokens[i]
                if re.match(cs.MOVE_REGEX_LAN, tok):
                    break
                i += 1

            tokens = tokens[i:]
            results = []

            for tok in tokens:
                if re.match(cs.MOVE_REGEX_LAN, tok):
                    results.append(tok.replace(":", ""))
                elif tok.isdigit():
                    results.append(int(tok))

            total = results.pop()
            perft_results = {}

            i = 0
            while i < len(results):
                perft_results[results[i]] = results[i + 1]
                i += 2

            return perft_results, total

    def get_perft_totals(self, depths, fen=cs.START_POS):
        """Returns the perft results up to a given depth."""
        if not depths:
            return []

        command = f"position fen {fen}\n"

        for d in depths:
            command += f"go perft {d}\n"

        command += "quit"

        with subprocess.Popen(
            [self.exec_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        ) as proc:
            output = proc.communicate(command)[0]
            lines = output.split("\n")
            totals = {}
            i = 0

            for l in lines:
                if re.match(cs.MOVE_REGEX_LAN, l):
                    continue

                tokens = l.split(":")

                if tokens[-1].strip().isdigit():
                    totals[depths[i]] = int(tokens[-1])
                    i += 1

            return totals

    def get_best_move(self, fen=cs.START_POS, t=10000):
        """Returns the best move found by the engine for the current position."""

        with subprocess.Popen(
            [self.exec_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        ) as proc:
            proc.stdin.write(f"position fen {fen}\ngo movetime {t}\n")
            proc.stdin.flush()
            time.sleep((t / 1000) + 1)

            proc.stdin.write("isready\nquit\n")
            proc.stdin.flush()
            lines = []

            while True:
                text = proc.stdout.readline().strip()

                if text == "readyok":
                    break

                if text != "":
                    lines.append(text)

            return lines[-1].split(" ")[1]
