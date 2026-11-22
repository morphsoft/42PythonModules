*This project has been created as part of the 42 curriculum by hvaini-d, <login2>.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. It reads a configuration
file, generates a random (but reproducible) maze, writes it to a file using a
hexadecimal wall encoding, and shows it in the terminal with an interactive
menu.

Every maze:

- has walls on the whole external border and coherent walls between cells;
- is fully connected (every cell can be reached), except the cells of the
  **"42"** drawn in the middle with fully closed cells;
- never has an open area of 3x3 cells or more.

Two modes are available:

| Mode | Config | Result |
|------|--------|--------|
| Perfect | `PERFECT=True` | exactly one path between any two cells (no loop) |
| Pac-Man | `PERFECT=False` | a playable board: no dead-end, several loops, corners and centre open |

## Instructions

Requirements: Python 3.10 or later.

```bash
make install        # installs flake8, mypy, pytest and build
make run            # python3 a_maze_ing.py config.txt
make debug          # same, inside pdb
make lint           # flake8 + mypy (mandatory flags)
make lint-strict    # flake8 + mypy --strict
make test           # unit tests (pytest)
make tester         # guided tour: checks every subject rule, explained
make package        # builds mazegen-1.0.0-py3-none-any.whl at the root
make clean          # removes caches
```

Or directly:

```bash
python3 a_maze_ing.py config.txt
```

Menu shown under the maze:

```
1. Re-generate a new maze      (new random seed, file rewritten)
2. Show / Hide the shortest path
3. Rotate the wall colours     (the "42" changes colour too)
4. Quit
```

Colours: entry = magenta, exit = red, shortest path = cyan.

## Configuration file

One `KEY=VALUE` per line. Lines starting with `#` and empty lines are
ignored. Keys are not case sensitive.

| Key | Mandatory | Description | Example |
|-----|-----------|-------------|---------|
| `WIDTH` | yes | width in cells (2 to 100) | `WIDTH=20` |
| `HEIGHT` | yes | height in cells (2 to 100) | `HEIGHT=15` |
| `ENTRY` | yes | entry cell `x,y` | `ENTRY=0,0` |
| `EXIT` | yes | exit cell `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | where to write the maze | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `True` or `False` | `PERFECT=False` |
| `SEED` | no | integer; same seed = same maze. Random if absent | `SEED=42` |

`(0,0)` is the top-left cell. Entry and exit must be different, inside the
maze, and not on the "42". Unknown keys, duplicated keys, missing keys and
bad values are reported with a clear error message.

If the maze is too small for the "42" (smaller than 9x7), it is skipped and
an error message is printed.

### Output file

One hexadecimal digit per cell, one line per row. Each bit is a closed wall:
North = 1, East = 2, South = 4, West = 8. Then an empty line, the entry,
the exit and the shortest path written with `N`, `E`, `S`, `W`:

```
9515395...
...

0,0
19,14
SSEEESSSSSESWSSW...
```

## Maze generation algorithm

**Recursive backtracker** (randomized depth-first search), written with a
stack instead of recursion:

1. Start with every wall closed, and mark the "42" cells as forbidden.
2. From the entry, pick a random unvisited neighbour, open the wall, move.
3. When there is no unvisited neighbour, go back one step (pop the stack).
4. Stop when the stack is empty: every free cell has been visited.

This gives a **perfect maze** (a spanning tree). For the Pac-Man mode
(`PERFECT=False`) we then "braid" it: every dead-end gets one extra wall
opened (which always creates a loop and never a new dead-end), refusing any
opening that would create a 3x3 open area. If fewer than 2 loops exist, more
walls are opened.

The shortest path is found with a **breadth-first search** (BFS).

### Why this algorithm

- It is short and easy to explain: "walk randomly, go back when stuck".
- It produces long winding corridors, which look nice.
- Skipping the "42" is trivial: those cells are simply marked as visited.
- It always produces a perfect maze, and braiding a perfect maze is an
  easy way to get the Pac-Man board.

## Reusable code

The whole generator lives in the `mazegen/` package, in a single class
`MazeGenerator` that knows nothing about the config file or the terminal.
It is packaged as `mazegen-1.0.0-py3-none-any.whl` (at the root of the
repository) and can be rebuilt with `make package` (needs `pip install build`).

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

```python
from mazegen import MazeGenerator, EAST

# Basic use
maze = MazeGenerator(20, 15)          # random seed, Pac-Man mode
maze.generate()

# Custom parameters
maze = MazeGenerator(width=30, height=20, entry=(0, 0), exit_=(29, 19),
                     perfect=True, seed=42)
maze.generate()

# Access the structure
maze.grid[y][x]                       # int 0-15, bits N=1 E=2 S=4 W=8
maze.has_wall(3, 2, EAST)             # True / False
maze.pattern                          # set of (x, y) cells of the "42"

# Access a solution
maze.solve()                          # [(0, 0), (1, 0), ...]
maze.solution_letters()               # "ESSE..."
```

`config_reader.py`, `display.py` and `a_maze_ing.py` are specific to this
project and are not part of the package.

## Project structure

```
a_maze_ing.py      main program: config -> maze -> file -> menu
config_reader.py   reads and checks the configuration file
display.py         draws the maze in the terminal (ANSI colours)
mazegen/           the reusable package (MazeGenerator)
tests/             pytest unit tests + tester.py (guided terminal tester)
```

## Team and project management

- **Roles**:
  - hvaini-d: maze generation, packaging, tests.
  - <login2>: configuration parser, terminal display, README.
- **Planning**: first a single-file prototype, then split into small modules
  so that each part could be studied on its own. The Pac-Man mode was added
  when the subject was updated (v2.3).
- **What worked well**: writing one test per rule of the subject made it
  easy to check that every change kept the maze valid.
- **What could be improved**: an MLX graphical display, multiple
  algorithms, generation animation.
- **Tools**: VS Code, git, flake8, mypy, pytest, Claude Code.

## Resources

- [Maze generation algorithm - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Jamis Buck - Maze algorithms](https://weblog.jamisbuck.com/2011/2/7/maze-generation-algorithm-recap)
- [Breadth-first search - Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Braid mazes (Think Labyrinth)](https://www.astrolog.org/labyrnth/algrithm.htm)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Choose a license](https://choosealicense.com/licenses/mit/)

### How AI was used

Claude Code was used to:

- reorganise the code into small, commented modules;
- review the project against the subject, rule by rule;
- write the unit tests and the packaging files (pyproject.toml, Makefile);
- create a teaching guide used by the team to study the project.

Every part was read, run and discussed by the team before being kept.
