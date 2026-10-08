"""Seeded maze generator with a '42' pattern, perfect and Pac-Man modes.

Usage:
    python3 maze.py [config_file]        (default: config.txt)

Config file format (KEY=VALUE, '#' starts a comment):
    WIDTH=25            required, int
    HEIGHT=17           required, int
    ENTRY=0,0           required, x,y
    EXIT=24,16          required, x,y
    PERFECT=False       optional, default False (False = Pac-Man mode)
    RANDOM_SEED=42      optional, a random one is picked and printed if absent
    OUTPUT_FILE=maze.txt  optional, writes the maze + path to that file

Each cell is an int 0-15, one bit per closed wall (see N, E, S, W).
Coordinates are (x, y) with (0, 0) top-left; the grid is indexed grid[y][x].
"""

import random
import sys
from collections import deque
from dataclasses import dataclass
from typing import Optional, Union

N, E, S, W = 1, 2, 4, 8
ALL_WALLS = N | E | S | W

# (dx, dy, wall on my side, wall on the neighbour's side)
DIRECTIONS = [
    (0, -1, N, S),
    (1, 0, E, W),
    (0, 1, S, N),
    (-1, 0, W, E),
]
LETTERS = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}

Cell = tuple[int, int]
Grid = list[list[int]]

# The digits, as data. 'X' = fully closed cell, '.' = normal corridor cell.
# BIG has no 1-cell-wide pockets, so it forces no dead end in Pac-Man mode.
# SMALL is the fallback for small mazes (its 3 pockets are forced dead ends).
FONTS = [
    {
        "4": ["X..X", "X..X", "X..X", "XXXX", "...X", "...X", "...X"],
        "2": ["XXXX", "...X", "...X", "XXXX", "X...", "X...", "XXXX"],
    },
    {
        "4": ["X.X", "X.X", "XXX", "..X", "..X"],
        "2": ["XXX", "..X", "XXX", "X..", "XXX"],
    },
]

# Pac-Man mode: after removing dead ends, open roughly one more wall
# per this many cells, to add junctions. Raise it for fewer extra loops.
EXTRA_LOOP_RATIO = 30


class MazeError(Exception):
    """Any problem the user should see as a clean message, not a traceback."""


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

@dataclass
class MazeConfig:
    width: int
    height: int
    entry: Cell
    exit: Cell
    perfect: bool = False
    seed: Union[int, str, None] = None
    output_file: Optional[str] = None

    @classmethod
    def from_file(cls, path: str) -> "MazeConfig":
        """Read, convert and validate a KEY=VALUE config file."""
        raw: dict[str, str] = {}
        try:
            with open(path, "r") as file:
                for number, line in enumerate(file, start=1):
                    line = line.strip()          # strip FIRST: "\n" is truthy
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        raise MazeError(
                            f"{path}, line {number}: expected KEY=VALUE, "
                            f"got '{line}'")
                    key, value = line.split("=", 1)
                    raw[key.strip().upper()] = value.strip()
        except OSError as error:
            raise MazeError(f"cannot read '{path}': {error.strerror}")

        for key in ("WIDTH", "HEIGHT", "ENTRY", "EXIT"):
            if not raw.get(key):
                raise MazeError(f"missing required key {key} in {path}")

        config = cls(
            width=cls._to_int(raw, "WIDTH"),
            height=cls._to_int(raw, "HEIGHT"),
            entry=cls._to_cell(raw, "ENTRY"),
            exit=cls._to_cell(raw, "EXIT"),
            perfect=cls._to_bool(raw.get("PERFECT", "False")),
            seed=cls._to_seed(raw.get("RANDOM_SEED")),
            output_file=raw.get("OUTPUT_FILE") or None,
        )
        config.check()
        return config

    def check(self) -> None:
        if self.width < 2 or self.height < 2:
            raise MazeError("WIDTH and HEIGHT must both be at least 2")
        for name, (x, y) in (("ENTRY", self.entry), ("EXIT", self.exit)):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise MazeError(
                    f"{name} {x},{y} is outside the "
                    f"{self.width}x{self.height} maze")
        if self.entry == self.exit:
            raise MazeError("ENTRY and EXIT must be different cells")

    @staticmethod
    def _to_int(raw: dict[str, str], key: str) -> int:
        try:
            return int(raw[key])
        except ValueError:
            raise MazeError(f"{key} must be an integer, got '{raw[key]}'")

    @staticmethod
    def _to_cell(raw: dict[str, str], key: str) -> Cell:
        parts = raw[key].split(",")
        try:
            if len(parts) != 2:
                raise ValueError
            return (int(parts[0]), int(parts[1]))
        except ValueError:
            raise MazeError(f"{key} must look like 3,7 - got '{raw[key]}'")

    @staticmethod
    def _to_bool(text: str) -> bool:
        if text.lower() in ("true", "1", "yes", "on"):
            return True
        if text.lower() in ("false", "0", "no", "off"):
            return False
        raise MazeError(f"PERFECT must be True or False, got '{text}'")

    @staticmethod
    def _to_seed(text: Optional[str]) -> Union[int, str, None]:
        if not text:
            return None
        try:
            return int(text)
        except ValueError:
            return text                 # any string is a valid seed too


# --------------------------------------------------------------------------
# Shared helper
# --------------------------------------------------------------------------

def is_open_block(grid: Grid, left: int, top: int) -> bool:
    """True if the 3x3 block whose top-left cell is (left, top) has none
    of its 12 internal walls, i.e. it is a forbidden 3x3 open area."""
    for y in range(top, top + 3):
        for x in range(left, left + 3):
            if x < left + 2 and grid[y][x] & E:
                return False
            if y < top + 2 and grid[y][x] & S:
                return False
    return True


# --------------------------------------------------------------------------
# The maze itself
# --------------------------------------------------------------------------

class Maze:
    def __init__(self, config: MazeConfig) -> None:
        self.config = config
        self.width = config.width
        self.height = config.height
        self.entry = config.entry
        self.exit = config.exit
        self.perfect = config.perfect
        # No seed given: pick one ourselves so the run can still be replayed.
        self.seed = (config.seed if config.seed is not None
                     else random.randrange(2 ** 32))
        self.rng = random.Random(self.seed)     # the ONLY source of randomness
        self.grid: Grid = []
        self.blocked: set[Cell] = set()         # the cells drawing the 42
        self.notes: list[str] = []

    # ---- public -----------------------------------------------------------

    def generate_maze(self) -> Grid:
        self.grid = [[ALL_WALLS] * self.width for _ in range(self.height)]
        self.blocked = self._place_pattern()
        for name, cell in (("ENTRY", self.entry), ("EXIT", self.exit)):
            if cell in self.blocked:
                raise MazeError(
                    f"{name} {cell[0]},{cell[1]} falls on the 42 pattern, "
                    "pick another cell")
        self._carve()
        if not self.perfect:
            self._braid()
        return self.grid

    def is_free(self, x: int, y: int) -> bool:
        """Inside the grid and not part of the 42."""
        return (0 <= x < self.width and 0 <= y < self.height
                and (x, y) not in self.blocked)

    def free_cell_count(self) -> int:
        return self.width * self.height - len(self.blocked)

    def passage_count(self) -> int:
        """Open passages. Each is counted once, from its west/north cell."""
        return sum((not cell & E) + (not cell & S)
                   for row in self.grid for cell in row)

    def loop_count(self) -> int:
        """Independent loops: passages beyond those of a spanning tree."""
        return self.passage_count() - (self.free_cell_count() - 1)

    def dead_ends(self) -> list[Cell]:
        return [(x, y)
                for y in range(self.height) for x in range(self.width)
                if self.is_free(x, y) and self._is_dead_end(x, y)]

    # ---- the 42 -----------------------------------------------------------

    def _place_pattern(self) -> set[Cell]:
        """Return the cells of the 42, centred, or an empty set if the maze
        is too small. Runs BEFORE carving; the carver then avoids them."""
        # The gap between the digits is 1 column for odd widths and 2 for
        # even ones: that keeps the pattern exactly centred AND guarantees
        # the centre cell(s) of the maze land in the gap, i.e. stay open.
        gap = 1 if self.width % 2 else 2
        for font in FONTS:
            four, two = font["4"], font["2"]
            rows = [four[i] + "." * gap + two[i] for i in range(len(four))]
            stamp_w, stamp_h = len(rows[0]), len(rows)
            # At least one free cell all around, so nothing gets cut off.
            if self.width < stamp_w + 2 or self.height < stamp_h + 2:
                continue
            left = (self.width - stamp_w) // 2
            top = (self.height - stamp_h) // 2
            return {(left + x, top + y)
                    for y, row in enumerate(rows)
                    for x, char in enumerate(row) if char == "X"}
        self.notes.append("maze too small for the 42 pattern, skipped it")
        return set()

    # ---- perfect maze: randomized depth-first search ------------------------

    def _carve(self) -> None:
        visited = [[False] * self.width for _ in range(self.height)]
        for x, y in self.blocked:
            visited[y][x] = True         # the whole trick: never enter the 42
        start = self.entry
        visited[start[1]][start[0]] = True
        stack = [start]
        while stack:
            x, y = stack[-1]
            candidates = [
                (x + dx, y + dy, wall, opposite)
                for dx, dy, wall, opposite in DIRECTIONS
                if 0 <= x + dx < self.width and 0 <= y + dy < self.height
                and not visited[y + dy][x + dx]
            ]
            if not candidates:
                stack.pop()
                continue
            nx, ny, wall, opposite = self.rng.choice(candidates)
            self.open_passage(x, y, nx, ny, wall, opposite)
            visited[ny][nx] = True
            stack.append((nx, ny))

    def open_passage(self, x: int, y: int, nx: int, ny: int,
                     wall: int, opposite: int) -> None:
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~opposite

    def _close_passage(self, x: int, y: int, nx: int, ny: int,
                       wall: int, opposite: int) -> None:
        self.grid[y][x] |= wall
        self.grid[ny][nx] |= opposite

    # ---- Pac-Man mode: braiding ---------------------------------------------

    def _braid(self) -> None:
        """Turn the perfect maze into a Pac-Man board.

        Opening a wall between two already-connected cells always creates
        exactly one new loop and can never create a dead end, so:
          1. every dead end gets one extra opening (kills it, adds a loop);
          2. a few more random walls are opened for extra junctions;
          3. we make sure at least 2 loops exist whatever the maze size.
        Every opening goes through _try_open, which refuses 3x3 open areas.
        """
        cells = [(x, y) for y in range(self.height)
                 for x in range(self.width) if self.is_free(x, y)]
        self.rng.shuffle(cells)
        for x, y in cells:
            if not self._is_dead_end(x, y):
                continue                 # may have been fixed by a neighbour
            options = self._closed_walls(x, y)
            self.rng.shuffle(options)
            for nx, ny, wall, opposite in options:
                if self._try_open(x, y, nx, ny, wall, opposite):
                    break

        target = max(2, self.loop_count() + len(cells) // EXTRA_LOOP_RATIO)
        walls = [(x, y, nx, ny, wall, opposite)
                 for x, y in sorted(cells)
                 for nx, ny, wall, opposite in self._closed_walls(x, y)
                 if wall in (E, S)]      # E and S only: each wall listed once
        self.rng.shuffle(walls)
        for x, y, nx, ny, wall, opposite in walls:
            if self.loop_count() >= target:
                break
            self._try_open(x, y, nx, ny, wall, opposite)

        if self.loop_count() < 2:
            raise MazeError(
                "maze too small to hold 2 loops: enlarge it or set "
                "PERFECT=True")

    def _is_dead_end(self, x: int, y: int) -> bool:
        return bin(self.grid[y][x]).count("1") == 3

    def _closed_walls(self, x: int, y: int) -> list[tuple[int, int, int, int]]:
        """Closed walls of (x, y) that lead to another free cell, so never
        a border wall and never a wall of the 42."""
        return [(x + dx, y + dy, wall, opposite)
                for dx, dy, wall, opposite in DIRECTIONS
                if self.grid[y][x] & wall and self.is_free(x + dx, y + dy)]

    def _try_open(self, x: int, y: int, nx: int, ny: int,
                  wall: int, opposite: int) -> bool:
        """Open the wall, but undo it if that creates a 3x3 open area."""
        self.open_passage(x, y, nx, ny, wall, opposite)
        # Only the 3x3 blocks containing (x, y) can have been affected.
        for top in range(max(0, y - 2), min(y, self.height - 3) + 1):
            for left in range(max(0, x - 2), min(x, self.width - 3) + 1):
                if is_open_block(self.grid, left, top):
                    self._close_passage(x, y, nx, ny, wall, opposite)
                    return False
        return True


# --------------------------------------------------------------------------
# Shortest path (breadth-first search)
# --------------------------------------------------------------------------

class MazePathFinder:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    def find_path(self) -> list[Cell]:
        """Shortest entry -> exit path, or [] if the exit is unreachable."""
        previous = self._flood(self.maze.entry, stop_at=self.maze.exit)
        if self.maze.exit not in previous:
            return []
        path: list[Cell] = []
        cell: Optional[Cell] = self.maze.exit
        while cell is not None:          # walk backwards to the entry
            path.append(cell)
            cell = previous[cell]
        path.reverse()
        return path

    def reachable_count(self) -> int:
        """How many cells can be reached from the entry."""
        return len(self._flood(self.maze.entry))

    def _flood(self, start: Cell,
               stop_at: Optional[Cell] = None) -> dict[Cell, Optional[Cell]]:
        grid = self.maze.grid
        previous: dict[Cell, Optional[Cell]] = {start: None}
        queue = deque([start])
        while queue:
            x, y = queue.popleft()       # oldest first: that's what BFS is
            if (x, y) == stop_at:
                break
            for dx, dy, wall, _ in DIRECTIONS:
                neighbour = (x + dx, y + dy)
                if grid[y][x] & wall or neighbour in previous:
                    continue
                if not (0 <= neighbour[0] < self.maze.width
                        and 0 <= neighbour[1] < self.maze.height):
                    continue             # only possible if a border is broken
                previous[neighbour] = (x, y)
                queue.append(neighbour)
        return previous

    @staticmethod
    def as_directions(path: list[Cell]) -> str:
        """[(0,0), (1,0), (1,1)] -> 'ES'"""
        return "".join(LETTERS[(bx - ax, by - ay)]
                       for (ax, ay), (bx, by) in zip(path, path[1:]))


# --------------------------------------------------------------------------
# Validator: trusts nothing, re-checks every rule on the finished grid
# --------------------------------------------------------------------------

class MazeValidator:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    def validate(self) -> list[str]:
        """Return the list of broken rules (empty list = valid maze)."""
        maze, grid = self.maze, self.maze.grid
        w, h = maze.width, maze.height
        errors: list[str] = []

        for name, (x, y) in (("entry", maze.entry), ("exit", maze.exit)):
            if not maze.is_free(x, y):
                errors.append(f"{name} is out of bounds or on the 42")
        if maze.entry == maze.exit:
            errors.append("entry and exit are the same cell")
        if errors:
            return errors                # the checks below need a sane entry

        for y in range(h):
            for x in range(w):
                for dx, dy, wall, opposite in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    mine = bool(grid[y][x] & wall)
                    if not (0 <= nx < w and 0 <= ny < h):
                        if not mine:
                            errors.append(f"border open at {x},{y}")
                    elif mine != bool(grid[ny][nx] & opposite):
                        errors.append(f"incoherent wall {x},{y} / {nx},{ny}")

        for x, y in sorted(maze.blocked):
            if grid[y][x] != ALL_WALLS:
                errors.append(f"42 cell {x},{y} is not fully closed")

        reachable = MazePathFinder(maze).reachable_count()
        if reachable != maze.free_cell_count():
            errors.append(f"only {reachable} of {maze.free_cell_count()} "
                          "cells are reachable")

        for top in range(h - 2):
            for left in range(w - 2):
                if is_open_block(grid, left, top):
                    errors.append(f"3x3 open area at {left},{top}")

        if maze.perfect:
            if maze.loop_count() != 0:
                errors.append(f"perfect maze has {maze.loop_count()} loop(s)")
        else:
            if maze.loop_count() < 2:
                errors.append("Pac-Man maze needs at least 2 loops")
            spots = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
                     (w // 2, h // 2), ((w - 1) // 2, (h - 1) // 2)]
            for x, y in spots:
                if not maze.is_free(x, y):
                    errors.append(f"corner/centre cell {x},{y} is not open")
        return errors


# --------------------------------------------------------------------------
# Terminal rendering
# --------------------------------------------------------------------------

class MazeVisualizer:
    RESET = "\033[0m"
    WALL = "\033[97m██" + RESET      # bright white block
    OPEN = "  "
    SOLID = "\033[93m██" + RESET     # yellow: fully closed cells (the 42)
    ENTRY = "\033[42m  " + RESET     # green background
    EXIT = "\033[41m  " + RESET      # red background
    PATH = "\033[96m••" + RESET      # cyan dots

    def render(self, grid: Grid, entry: Optional[Cell] = None,
               exit_: Optional[Cell] = None,
               path: Optional[list[Cell]] = None) -> str:
        """Return the maze as a printable string."""
        h, w = len(grid), len(grid[0])

        # Canvas is (2h+1) x (2w+1): cells sit at odd positions,
        # walls and corner pillars at the even ones. Start all wall.
        canvas = [[self.WALL] * (2 * w + 1) for _ in range(2 * h + 1)]

        for y in range(h):
            for x in range(w):
                cell = grid[y][x]
                cy, cx = 2 * y + 1, 2 * x + 1
                if cell == ALL_WALLS:               # sealed cell -> solid
                    canvas[cy][cx] = self.SOLID
                    continue
                canvas[cy][cx] = self.OPEN
                if not cell & N:
                    canvas[cy - 1][cx] = self.OPEN
                if not cell & S:
                    canvas[cy + 1][cx] = self.OPEN
                if not cell & W:
                    canvas[cy][cx - 1] = self.OPEN
                if not cell & E:
                    canvas[cy][cx + 1] = self.OPEN

        if path:
            for (x, y) in path:
                canvas[2 * y + 1][2 * x + 1] = self.PATH
            # the gap between two consecutive cells is their canvas midpoint
            for (ax, ay), (bx, by) in zip(path, path[1:]):
                canvas[ay + by + 1][ax + bx + 1] = self.PATH

        if entry:
            canvas[2 * entry[1] + 1][2 * entry[0] + 1] = self.ENTRY
        if exit_:
            canvas[2 * exit_[1] + 1][2 * exit_[0] + 1] = self.EXIT
        return "\n".join("".join(row) for row in canvas)


# --------------------------------------------------------------------------
# Output file
# --------------------------------------------------------------------------

def write_output(maze: Maze, path: list[Cell], filename: str) -> None:
    """One hex digit per cell, one line per row; then a blank line, the
    entry, the exit, and the shortest path as N/E/S/W letters.
    ASSUMED FORMAT - compare with your subject and adjust if needed."""
    try:
        with open(filename, "w") as file:
            for row in maze.grid:
                file.write("".join(f"{cell:X}" for cell in row) + "\n")
            file.write("\n")
            file.write(f"{maze.entry[0]},{maze.entry[1]}\n")
            file.write(f"{maze.exit[0]},{maze.exit[1]}\n")
            file.write(MazePathFinder.as_directions(path) + "\n")
    except OSError as error:
        raise MazeError(f"cannot write '{filename}': {error.strerror}")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.txt"
    try:
        config = MazeConfig.from_file(config_path)
        maze = Maze(config)
        maze.generate_maze()

        problems = MazeValidator(maze).validate()
        if problems:
            raise MazeError("generated maze is invalid:\n  - "
                            + "\n  - ".join(problems))

        path = MazePathFinder(maze).find_path()
        print(MazeVisualizer().render(maze.grid, maze.entry, maze.exit, path))
        print(f"\n{maze.width}x{maze.height}, "
              f"{'perfect' if maze.perfect else 'Pac-Man'} mode, "
              f"seed {maze.seed}")
        print(f"loops: {maze.loop_count()}, "
              f"dead ends: {len(maze.dead_ends())}, "
              f"shortest path: {len(path) - 1} steps")
        for note in maze.notes:
            print(f"note: {note}")

        if config.output_file:
            write_output(maze, path, config.output_file)
            print(f"written to {config.output_file}")
    except MazeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())