import random
from collections import deque

N, E, S, W = 1, 2, 4, 8
DIRECTIONS = [
    (0, -1, N, S),   # going north: my N wall, neighbour's S wall
    (1, 0, E, W),
    (0, 1, S, N),
    (-1, 0, W, E),
]

class Maze:
    def __init__(self):
        self.config = {}
        self.random_seed = None
        self.grid = None
        self.entry = None
        self.exit = None
        self.path = None
        self.rng = random.Random()

    def read_config(self):
        # Read the maze condiguration file from config.txt file
        with open("config.txt", "r") as file:
            for line in file:
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"Error: Invalid line in config file: {line.strip()}")
                key, value = line.strip().split("=", 1)
                self.config[key.strip()] = value.strip()
        if (self.config.get("RANDOM") == "True"):
            self.random_seed = self.config.get("RANDOM_SEED")
            self.rng.seed(self.random_seed)
        self.entry = tuple(map(int, self.config.get("ENTRY").split(","))) if self.config.get("ENTRY") else None
        self.exit = tuple(map(int, self.config.get("EXIT").split(","))) if self.config.get("EXIT") else None
        self.path = None
        return self.config

    def generate_maze(self):
        if not self.config:
            raise ValueError("Error: Configuration not loaded.")
        self.grid = self.generate_grid()
        self.carve()
        return self.grid

    def generate_grid(self):
        if not self.config:
            raise ValueError("Error: Configuration not loaded.")
        width = int(self.config.get("WIDTH"))
        height = int(self.config.get("HEIGHT"))
        grid = [[15 for _ in range(width)] for _ in range(height)]
        return grid

    def return_grid(self):
        if not self.config:
            raise ValueError("Error: Configuration not loaded.")
        return self.grid

    def generate_grid_visual_representation(self):
        if not self.config:
            raise ValueError("Error: Configuration not loaded.")
        return MazeVisualizer().render(self.grid, entry=self.entry, exit_=self.exit)

    def carve(self):
        grid = self.grid
        width, height = len(grid[0]), len(grid)
        visited = [[False] * width for _ in range(height)]
        start = tuple(self.entry)
        visited[start[1]][start[0]] = True
        stack = [start]
        while stack:
            x, y = stack[-1]
            candidates = [
                (x + dx, y + dy, wall, opposite)
                for dx, dy, wall, opposite in DIRECTIONS
                if 0 <= x + dx < width and 0 <= y + dy < height
                and not visited[y + dy][x + dx]
            ]
            if not candidates:
                stack.pop()
                continue
            nx, ny, wall, opposite = self.rng.choice(candidates)
            self.open_passage(x, y, nx, ny, wall, opposite)
            visited[ny][nx] = True
            stack.append((nx, ny))

    def open_passage(self, x, y, nx, ny, wall, opposite):
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~opposite

class MazePathFinder:
    def __init__(self, maze : Maze):
        self.maze = maze

    def find_path(self):
        grid = self.maze.grid
        start = tuple(self.maze.entry)
        goal = tuple(self.maze.exit)
        previous = {start: None}          # cell -> the cell we reached it from
        queue = deque([start])

        while queue:
            x, y = queue.popleft()        # oldest first: this is what makes it BFS
            if (x, y) == goal:
                break
            for dx, dy, wall, _ in DIRECTIONS:
                neighbour = (x + dx, y + dy)
                if grid[y][x] & wall:     # wall in the way: can't go there
                    continue
                if neighbour in previous: # already reached by a shorter route
                    continue
                previous[neighbour] = (x, y)
                queue.append(neighbour)

        if goal not in previous:
            return []                     # exit unreachable

        path = []
        cell = goal
        while cell is not None:           # walk backwards to the start
            path.append(cell)
            cell = previous[cell]
        path.reverse()
        return path

class MazeVisualizer:
    RESET = "\033[0m"
    WALL = "\033[97m██" + RESET      # bright white block
    OPEN = "  "
    SOLID = "\033[93m██" + RESET     # yellow: fully closed cells (the 42)
    ENTRY = "\033[42m  " + RESET     # green background
    EXIT = "\033[41m  " + RESET      # red background
    PATH = "\033[96m••" + RESET      # cyan dots


    def render(self, grid, entry=None, exit_=None, path=None):
        """Return the maze as a printable string."""
        h, w = len(grid), len(grid[0])

        # Canvas is (2h+1) x (2w+1): cells sit at odd positions,
        # walls and corner pillars at the even ones. Start all wall.
        canvas = [[self.WALL] * (2 * w + 1) for _ in range(2 * h + 1)]

        for y in range(h):
            for x in range(w):
                cell = grid[y][x]
                cy, cx = 2 * y + 1, 2 * x + 1
                if cell == 15:                      # sealed cell -> solid block
                    canvas[cy][cx] = self.SOLID
                    continue
                canvas[cy][cx] = self.OPEN
                if not cell & N:
                    canvas[cy - 1][cx] = self.OPEN
                if not cell & S:
                    canvas[cy + 1][cx] = self.OPEN
                if not cell & W:
                    canvas[cy][cx - 1] = self.OPEN
                if not cell &  E:
                    canvas[cy][cx + 1] = self.OPEN

        if path:
            for (x, y) in path:
                canvas[2 * y + 1][2 * x + 1] = self.PATH
            for (ax, ay), (bx, by) in zip(path, path[1:]):
                canvas[ay + by + 1][ax + bx + 1] = self.PATH

        if entry:
            canvas[2 * entry[1] + 1][2 * entry[0] + 1] = self.ENTRY
        if exit_:
            canvas[2 * exit_[1] + 1][2 * exit_[0] + 1] = self.EXIT
        return "\n".join("".join(row) for row in canvas)

if __name__ == "__main__":
    maze = Maze()
    maze.read_config()
    grid = maze.generate_maze()
    maze.grid = grid  # store the generated grid in the maze instance
    visual_grid = maze.generate_grid_visual_representation()
    print(visual_grid)
    path_finder = MazePathFinder(maze)
    path = path_finder.find_path()
    visualizer = MazeVisualizer()
    print(visualizer.render(grid, entry=maze.entry, exit_=maze.exit, path=path))