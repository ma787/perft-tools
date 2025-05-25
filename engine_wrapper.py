import pexpect

import constants as cs


class EngineWrapper:
    """Class providing methods to control the engine process."""

    def __init__(self, engine_exec):
        self.proc = pexpect.spawn(f"{engine_exec}")
        self.proc.setecho(False)
        self.proc.sendline("uci")
        self.proc.expect(cs.NAME_REGEX)
        name_list = self.proc.after.decode("UTF-8").split("\r\n")[0].split(" ")
        self.name = " ".join(name_list[2:])

    def set_position(self, fen, moves=None):
        """Sets the current position that the engine should analyse."""
        if not moves:
            self.proc.sendline(f"position fen {fen}")
        else:
            self.proc.sendline(f"position fen {fen} moves {" ".join(moves)}")

    def close(self):
        """Ends the engine process."""
        self.proc.close()
