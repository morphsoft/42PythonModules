"""mazegen - gerador de labirintos reutilizável.

Uso rápido::

    from mazegen import MazeGenerator

    maze = MazeGenerator(20, 15, seed=42)
    maze.generate()
    print(maze.solution_letters())
"""

from mazegen.generator import (ALL_WALLS, EAST, NORTH, SOUTH, WEST,
                               MazeGenerator)

__all__ = ["MazeGenerator", "NORTH", "EAST", "SOUTH", "WEST", "ALL_WALLS"]
__version__ = "1.0.0"
