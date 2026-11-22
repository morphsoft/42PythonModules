"""Testes do projeto: rodam com ``make test`` (ou ``python3 -m pytest``).

Cada teste confere UMA regra do subject. Não são avaliados, mas
avisam na hora se alguma mudança quebrou uma regra.
"""

from pathlib import Path

import pytest

from config_reader import load_config
from mazegen import ALL_WALLS, MazeGenerator
from mazegen.generator import DIRECTIONS

SIZES = [(20, 15), (21, 16), (9, 7), (5, 5), (40, 30)]


def make(width: int, height: int, perfect: bool,
         seed: int = 1) -> MazeGenerator:
    """Atalho: cria e gera um labirinto."""
    maze = MazeGenerator(width, height, perfect=perfect, seed=seed)
    maze.generate()
    return maze


def reachable(maze: MazeGenerator) -> int:
    """Quantas células dá para alcançar a partir da entrada."""
    seen = {maze.entry}
    todo = [maze.entry]
    while todo:
        x, y = todo.pop()
        for dx, dy, wall, _, _ in DIRECTIONS:
            nxt = (x + dx, y + dy)
            if not maze.has_wall(x, y, wall) and nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return len(seen)


@pytest.mark.parametrize("perfect", [True, False])
@pytest.mark.parametrize("width,height", SIZES)
def test_walls_are_coherent_and_borders_closed(
        width: int, height: int, perfect: bool) -> None:
    maze = make(width, height, perfect)
    for y in range(height):
        for x in range(width):
            for dx, dy, wall, opposite, _ in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    assert (maze.has_wall(x, y, wall)
                            == maze.has_wall(nx, ny, opposite))
                else:
                    assert maze.has_wall(x, y, wall)


@pytest.mark.parametrize("perfect", [True, False])
@pytest.mark.parametrize("width,height", SIZES)
def test_connected_no_3x3_and_42_closed(
        width: int, height: int, perfect: bool) -> None:
    maze = make(width, height, perfect)
    free = width * height - len(maze.pattern)
    assert reachable(maze) == free
    for x, y in maze.pattern:
        assert maze.grid[y][x] == ALL_WALLS
    for top in range(height - 2):
        for left in range(width - 2):
            assert not maze._is_open_3x3(left, top)


@pytest.mark.parametrize("width,height", SIZES)
def test_perfect_has_no_loop(width: int, height: int) -> None:
    assert make(width, height, perfect=True).count_loops() == 0


@pytest.mark.parametrize("seed", range(10))
def test_pacman_board(seed: int) -> None:
    maze = make(20, 15, perfect=False, seed=seed)
    assert maze.count_loops() >= 2
    assert maze.count_dead_ends() <= 2
    w, h = maze.width, maze.height
    for cell in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
                 (w // 2, h // 2), ((w - 1) // 2, (h - 1) // 2)]:
        assert maze.is_free(*cell)


def test_42_present_or_skipped() -> None:
    assert make(20, 15, True).has_pattern
    assert make(9, 7, True).has_pattern
    assert not make(5, 5, True).has_pattern


def test_same_seed_same_maze() -> None:
    assert make(20, 15, False, 7).grid == make(20, 15, False, 7).grid
    assert make(20, 15, False, 7).grid != make(20, 15, False, 8).grid


def test_solution_walks_from_entry_to_exit() -> None:
    maze = make(20, 15, perfect=True)
    x, y = maze.entry
    moves = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    for letter in maze.solution_letters():
        dx, dy = moves[letter]
        x, y = x + dx, y + dy
    assert (x, y) == maze.exit


def test_hex_lines() -> None:
    maze = make(20, 15, perfect=True)
    lines = maze.to_hex_lines()
    assert len(lines) == 15
    assert all(len(line) == 20 for line in lines)


@pytest.mark.parametrize("kwargs", [
    {"width": 1, "height": 5},
    {"width": 5, "height": 5, "entry": (5, 0)},
    {"width": 5, "height": 5, "entry": (4, 4)},
])
def test_bad_parameters(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        MazeGenerator(**kwargs)  # type: ignore[arg-type]


def test_too_small_for_pacman() -> None:
    with pytest.raises(ValueError):
        make(2, 2, perfect=False)


def test_entry_on_42() -> None:
    # 20x15: o 42 (fonte grande, 10x7) começa em (5, 4), que é um "X".
    maze = MazeGenerator(20, 15, entry=(5, 4), seed=1)
    with pytest.raises(ValueError):
        maze.generate()


GOOD = "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n" \
       "OUTPUT_FILE=maze.txt\nPERFECT=True\n"


@pytest.mark.parametrize("content", [
    GOOD.replace("WIDTH=20\n", ""),             # chave faltando
    GOOD.replace("WIDTH=20", "WIDTH=abc"),      # não é número
    GOOD.replace("ENTRY=0,0", "ENTRY=0"),       # coordenada ruim
    GOOD.replace("PERFECT=True", "PERFECT=yes"),
    GOOD + "COLOR=red\n",                       # chave desconhecida
    GOOD + "WIDTH=3\n",                         # repetida
    GOOD + "nonsense\n",                        # sem "="
    GOOD.replace("WIDTH=20", "WIDTH=1000"),     # grande demais
])
def test_bad_config(tmp_path: Path, content: str) -> None:
    path = tmp_path / "config.txt"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_config(str(path))


def test_good_config(tmp_path: Path) -> None:
    path = tmp_path / "config.txt"
    path.write_text("# comment\n\n" + GOOD + "SEED=3\n")
    config = load_config(str(path))
    assert config.width == 20 and config.perfect and config.seed == 3


def test_missing_config_file() -> None:
    with pytest.raises(ValueError):
        load_config("does_not_exist.txt")
