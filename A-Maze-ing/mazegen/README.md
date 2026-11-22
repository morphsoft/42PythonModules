# mazegen

A small, dependency-free maze generator. Each maze is a rectangular grid,
with a "42" drawn in the middle by fully closed cells (when the maze is big
enough). Two modes:

- **perfect** (`perfect=True`): exactly one path between any two cells.
- **Pac-Man** (`perfect=False`, default): no dead-ends, several loops,
  corners and centre always open.

## Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Basic example

```python
from mazegen import MazeGenerator

maze = MazeGenerator(20, 15)      # random seed, Pac-Man mode
maze.generate()
print(maze.seed)                  # keep it to get the same maze again
```

## Custom parameters

```python
maze = MazeGenerator(
    width=30, height=20,          # size in cells (minimum 2x2)
    entry=(0, 0), exit_=(29, 19), # default: top-left -> bottom-right
    perfect=True,                 # single path, no loops
    seed=42,                      # same seed = same maze
)
maze.generate()
```

Invalid parameters raise `ValueError` with a readable message.

## Access the structure and a solution

```python
from mazegen import NORTH, EAST, SOUTH, WEST

maze.grid[y][x]                   # int 0-15, one bit per closed wall:
                                  # NORTH=1, EAST=2, SOUTH=4, WEST=8
maze.has_wall(3, 2, EAST)         # True / False
maze.pattern                      # set of (x, y) cells drawing the "42"

maze.solve()                      # shortest path: [(0, 0), (1, 0), ...]
maze.solution_letters()           # same path as "ESSE..."
maze.to_hex_lines()               # ["9515...", ...] one hex digit per cell
maze.count_loops()                # 0 for a perfect maze
maze.count_dead_ends()
```
