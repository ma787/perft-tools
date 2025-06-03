# perft-tools
This repository provides tools to make debugging a chess engine less time-consuming.

The **compare_perft** script allows you to compare your engine's move generation to a trusted engine (Stockfish)
at any node. This is shown in a table which compares the number of nodes after making each legal move, making
it easier to walk down the tree and isolate move generation bugs.

The **test_perft** script compares an engine's perft results to those stored in an EPD file. See [here](https://github.com/ChrisWhittington/Chess-EPDs/blob/master/perft.epd) for an example of an EPD file in the correct format. For each fen string stored in the file,
the script prints the difference between the engine's perft result at each recorded depth and the corresponding result stored in the file.

The **test_engine** script lets you test an engine's search and evaluation using results stored in an EPD file.
For each FEN string stored in the file, the engine is asked to search for a given amount of time (10s by default) and
the best move it returns is compared to those stored in the file.

## Requirements
**Stockfish** must be installed and accessible from your PATH (for the **compare_perft** script).

Your engine must recognise the following UCI commands:
- `go perft`
- `go movetime` (for the **test_engine** script)
- `position`
- `uci`

The engine must also output its perft results in a specific format for this script to work.
The moves should be in the format `[start square][destination square][promotion]` and followed by the
perft result after making that move. The total number of nodes should also be outputted, with a blank
line between the move list and the total. For example, `go perft 1` from the starting
position should output the following:

```
b1c3 1
b1a3 1
g1h3 1
g1f3 1
a2a3 1
a2a4 1
b2b3 1
b2b4 1
c2c3 1
c2c4 1
d2d3 1
d2d4 1
e2e3 1
e2e4 1
f2f3 1
f2f4 1
g2g3 1
g2g4 1
h2h3 1
h2h4 1

20
```

## compare_perft
This is an interactive CLI tool which takes the path to your engine executable as an argument.
It allows you to compare perft results with Stockfish at a given node.
You can also move up and down the game tree, making it easier to track move generation bugs which arise
deep in the tree.

### Usage
To run the tool:

`python PATH_TO_SCRIPT/compare_perft.py PATH_TO_ENGINE_EXECUTABLE`

#### Commands
`position [fen FEN | startpos ]  moves <MOVE_1> .... <MOVE_I>`

Updates the internal board representation of your engine and Stockfish to the specified position. Identical to the UCI command.

`diff DEPTH`

Displays a table comparing your engine's perft results at the given depth to Stockfish.

`move MOVE`

Updates the engines' positions by making the specified move. Must run diff first before using this command.

`back | b`

Unmakes a move, stepping back up the game tree.

## test_perft
This tool allows you to compare your engine's perft results to those stored in an EPD file.
It displays a table, showing the differences in results at each depth for each FEN stored in the file.

### Usage
To run the tool:

`python PATH_TO_SCRIPT/test_perft.py PATH_TO_ENGINE_EXECUTABLE PATH_TO_EPD_FILE <MAX_DEPTH>`

The script won't test perft results at a greater depth than MAX_DEPTH, if it is provided.

## test_engine
This tool compares the best moves submitted by an engine to those stored in an EPD file.
It prints the results for each position and records the number of passes/failures.

### Usage
To run the tool:

`python PATH_TO_SCRIPT/test_engine.py PATH_TO_ENGINE_EXECUTABLE PATH_TO_EPD_FILE <MOVETIME>`

The script will send the command `go movetime MOVETIME` to the engine for each test, where MOVETIME is 10000 by default.