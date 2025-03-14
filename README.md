# perft-tools
This repository provides to make debugging a chess engine's move generation less time-consuming.

The **compare_perft** script allows you to compare your engine's move generation to a trusted engine (Stockfish)
at any node. This is shown in a table which compares the number of nodes after making each legal move, making
it easier to walk down the tree and isolate move generation bugs.

The **test_perft** script lets you use an EPD file as the source of the perft results. A file containing some
standard perft results is provided in this repository for reference. For each FEN string stored in this file,
the script tests the engine's result at each depth stored for this entry and displays the difference.

## Requirements
**Stockfish** must be installed and accessible from your PATH (for the **compare_perft** script).

Your engine must recognise the following UCI commands:
- go perft DEPTH
- position
- uci

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
