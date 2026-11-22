#!/usr/bin/env python3
"""Tester do A-Maze-ing: uma visita guiada pelas 9 salas do labirinto.

Cada "sala" confere uma parte do subject e explica, no próprio terminal,
o que está sendo testado e por quê. No fim aparece o placar.

Uso (na raiz do projeto):
    python3 tests/tester.py              # visita completa
    python3 tests/tester.py --fast       # menos labirintos, sem lint/build
    python3 tests/tester.py --only 3 6   # só as salas 3 e 6
    python3 tests/tester.py --no-color   # sem cores nem animação

Diferente do ``test_maze.py`` (pytest), este tester confere o labirinto
"por fora": ele relê a grade de paredes com o próprio código dele, roda o
programa como o avaliador faria e lê o arquivo de saída byte a byte.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import zipfile
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator, Mapping, Optional

# A raiz do projeto é a pasta "pai" de tests/.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from config_reader import load_config  # noqa: E402
    from mazegen import MazeGenerator  # noqa: E402
except ImportError as import_error:
    print(f"Não consegui importar o projeto: {import_error}")
    print("Rode o tester a partir da raiz: python3 tests/tester.py")
    sys.exit(1)

Cell = tuple[int, int]
Grid = list[list[int]]

# --------------------------------------------------------------------------
# Paredes, do jeito do subject (conferidas aqui de forma independente)
# --------------------------------------------------------------------------

WALL = {"N": 1, "E": 2, "S": 4, "W": 8}
STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
CLOSED = 15
MANDATORY_MYPY_FLAGS = [
    "--warn-return-any", "--warn-unused-ignores", "--ignore-missing-imports",
    "--disallow-untyped-defs", "--check-untyped-defs",
]

# --------------------------------------------------------------------------
# Cores e estilo
# --------------------------------------------------------------------------

STYLES = {
    "bold": "1", "dim": "2", "italic": "3", "red": "91", "green": "92",
    "yellow": "93", "blue": "94", "magenta": "95", "cyan": "96",
    "grey": "90", "white": "97",
}
GRADIENT = ["95", "35", "94", "34", "96", "36", "92"]

# Letras gigantes do banner, 5 linhas cada.
BIG_LETTERS = {
    "A": [" ███ ", "█   █", "█████", "█   █", "█   █"],
    "M": ["█   █", "██ ██", "█ █ █", "█   █", "█   █"],
    "Z": ["█████", "   █ ", "  █  ", " █   ", "█████"],
    "E": ["█████", "█    ", "████ ", "█    ", "█████"],
    "I": ["███", " █ ", " █ ", " █ ", "███"],
    "N": ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
    "G": [" ████", "█    ", "█  ██", "█   █", " ███ "],
    "-": ["   ", "   ", "███", "   ", "   "],
}

PASS, FAIL, WARN, SKIP = "pass", "fail", "warn", "skip"
ICONS = {PASS: ("✔", "green"), FAIL: ("✘", "red"),
         WARN: ("⚠", "yellow"), SKIP: ("○", "grey")}
LINE_WIDTH = 66


@dataclass
class Check:
    """O resultado de um teste."""

    name: str
    status: str
    detail: str = ""
    hint: str = ""


@dataclass
class Room:
    """Uma sala do labirinto: um grupo de testes com uma história."""

    number: int
    icon: str
    title: str
    story: str
    run: Callable[["Tester"], None]
    checks: list[Check] = field(default_factory=list)

    def count(self, status: str) -> int:
        """Quantos testes desta sala terminaram com ``status``."""
        return sum(1 for check in self.checks if check.status == status)


class Tester:
    """Guarda as opções, imprime bonito e anota os resultados."""

    def __init__(self, color: bool, animate: bool, fast: bool) -> None:
        """Prepara o tester.

        Args:
            color: Usar cores ANSI.
            animate: Usar pequenas animações (só num terminal de verdade).
            fast: Modo rápido: menos labirintos e sem lint/build.
        """
        self.color = color
        self.animate = animate
        self.fast = fast
        self.room: Optional[Room] = None
        self.pending = False
        self.mazes: list[tuple[str, MazeGenerator]] = []
        self.workdir = Path(tempfile.mkdtemp(prefix="amazeing_tester_"))

    # ------------------------------ estilo ------------------------------

    def paint(self, text: str, *styles: str) -> str:
        """Pinta o texto com os estilos pedidos (se as cores estão ligadas)."""
        if not self.color or not styles:
            return text
        codes = ";".join(STYLES[name] for name in styles)
        return f"\033[{codes}m{text}\033[0m"

    def type_out(self, text: str, delay: float = 0.004) -> None:
        """Escreve o texto letra por letra, como numa máquina de escrever."""
        if not self.animate:
            print(text)
            return
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def wait(self, label: str) -> None:
        """Mostra 'rodando...' para algo demorado (some no próximo teste)."""
        if self.animate:
            sys.stdout.write(self.paint(f"     ⏳ {label}...", "dim"))
            sys.stdout.flush()
            self.pending = True

    def progress(self, label: str, done: int, total: int) -> None:
        """Barra de progresso que se redesenha na mesma linha."""
        if not self.animate:
            return
        size = 24
        filled = size * done // max(total, 1)
        bar = "▓" * filled + "░" * (size - filled)
        sys.stdout.write(
            f"\r     {self.paint(bar, 'cyan')} {done}/{total} {label}\033[K")
        sys.stdout.flush()
        self.pending = True

    def _clear_pending(self) -> None:
        """Apaga a linha de 'rodando...' ou da barra de progresso."""
        if self.pending:
            sys.stdout.write("\r\033[K")
            self.pending = False

    # ----------------------------- resultados ---------------------------

    def record(self, name: str, status: str, count: str = "",
               detail: str = "", hint: str = "") -> None:
        """Anota um resultado e imprime a linha dele."""
        assert self.room is not None
        self._clear_pending()
        self.room.checks.append(Check(name, status, detail, hint))
        icon, color = ICONS[status]
        dots = max(2, LINE_WIDTH - len(name) - len(count))
        leader = self.paint(" " + "·" * dots + " ", "grey")
        tail = self.paint(count, color) if count else ""
        print(f"  {self.paint(icon, color, 'bold')}  {name}{leader}{tail}")
        if detail and status != PASS:
            for line in detail.splitlines()[:6]:
                print(self.paint(f"       └─ {line}", color))
        if hint and status in (FAIL, WARN):
            print(self.paint(f"       💡 {hint}", "yellow", "dim"))

    def check(self, name: str, ok: bool, count: str = "", detail: str = "",
              hint: str = "", bonus: bool = False) -> bool:
        """Anota um teste: passou ou falhou (ou só avisa, se for bônus)."""
        status = PASS if ok else (WARN if bonus else FAIL)
        self.record(name, status, count, detail, hint)
        return ok

    def skip(self, name: str, reason: str) -> None:
        """Anota um teste que não deu para rodar."""
        self.record(name, SKIP, "pulado", reason)

    def note(self, text: str) -> None:
        """Um comentário do guia, entre os testes."""
        self._clear_pending()
        lines = textwrap.wrap(text, LINE_WIDTH - 4)
        for number, line in enumerate(lines):
            mark = "✎" if number == 0 else " "
            print(self.paint(f"     {mark} {line}", "magenta", "italic"))


class Tally:
    """Conta quantos labirintos passaram numa regra e guarda o 1º erro."""

    def __init__(self) -> None:
        """Começa zerado."""
        self.passed = 0
        self.total = 0
        self.first_problem = ""

    def add(self, problem: Optional[str], label: str) -> None:
        """Soma um labirinto. ``problem`` é None se estava tudo certo."""
        self.total += 1
        if problem is None:
            self.passed += 1
        elif not self.first_problem:
            self.first_problem = f"{label}: {problem}"

    @property
    def ok(self) -> bool:
        """True se todos passaram."""
        return self.passed == self.total

    @property
    def score(self) -> str:
        """Texto tipo '64/64'."""
        return f"{self.passed}/{self.total}"


# --------------------------------------------------------------------------
# Leitura independente de uma grade de paredes
# --------------------------------------------------------------------------

def open_neighbours(grid: Grid, x: int, y: int) -> Iterator[Cell]:
    """As vizinhas para onde dá para andar (parede aberta, dentro da grade)."""
    height, width = len(grid), len(grid[0])
    for letter, (dx, dy) in STEP.items():
        nx, ny = x + dx, y + dy
        if not grid[y][x] & WALL[letter] and 0 <= nx < width \
                and 0 <= ny < height:
            yield nx, ny


def border_hole(grid: Grid) -> Optional[str]:
    """Procura um buraco na borda externa. None = borda toda fechada."""
    height, width = len(grid), len(grid[0])
    for x in range(width):
        if not grid[0][x] & WALL["N"]:
            return f"célula ({x},0) aberta para o norte"
        if not grid[height - 1][x] & WALL["S"]:
            return f"célula ({x},{height - 1}) aberta para o sul"
    for y in range(height):
        if not grid[y][0] & WALL["W"]:
            return f"célula (0,{y}) aberta para o oeste"
        if not grid[y][width - 1] & WALL["E"]:
            return f"célula ({width - 1},{y}) aberta para o leste"
    return None


def incoherent_wall(grid: Grid) -> Optional[str]:
    """Procura duas vizinhas que discordam sobre a parede entre elas."""
    height, width = len(grid), len(grid[0])
    for y in range(height):
        for x in range(width):
            if x + 1 < width and bool(grid[y][x] & WALL["E"]) != bool(
                    grid[y][x + 1] & WALL["W"]):
                return f"({x},{y}) leste ≠ ({x + 1},{y}) oeste"
            if y + 1 < height and bool(grid[y][x] & WALL["S"]) != bool(
                    grid[y + 1][x] & WALL["N"]):
                return f"({x},{y}) sul ≠ ({x},{y + 1}) norte"
    return None


def distances(grid: Grid, start: Cell) -> dict[Cell, int]:
    """BFS: a distância de ``start`` até cada célula alcançável."""
    dist = {start: 0}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for nxt in open_neighbours(grid, x, y):
            if nxt not in dist:
                dist[nxt] = dist[(x, y)] + 1
                queue.append(nxt)
    return dist


def open_3x3(grid: Grid) -> Optional[Cell]:
    """Procura um quadrado 3x3 sem nenhuma parede dentro dele."""
    height, width = len(grid), len(grid[0])
    for top in range(height - 2):
        for left in range(width - 2):
            east_open = all(not grid[top + j][left + i] & WALL["E"]
                            for j in range(3) for i in range(2))
            south_open = all(not grid[top + j][left + i] & WALL["S"]
                             for j in range(2) for i in range(3))
            if east_open and south_open:
                return left, top
    return None


def free_cells(grid: Grid, blocked: set[Cell]) -> set[Cell]:
    """Todas as células que não são do 42."""
    return {(x, y) for y in range(len(grid)) for x in range(len(grid[0]))
            if (x, y) not in blocked}


def count_loops(grid: Grid, cells: set[Cell]) -> int:
    """Loops independentes = passagens - (células - 1)."""
    passages = 0
    for x, y in cells:
        if (x + 1, y) in cells and not grid[y][x] & WALL["E"]:
            passages += 1
        if (x, y + 1) in cells and not grid[y][x] & WALL["S"]:
            passages += 1
    return passages - (len(cells) - 1)


def dead_ends(grid: Grid, cells: set[Cell]) -> tuple[list[Cell], int]:
    """Becos sem saída: células com 3 paredes fechadas.

    Igual ao maze_analyzer.py: um beco só é "de verdade" se uma das paredes
    fechadas dá para uma célula normal (dava para abrir). Se todas dão para
    o 42 ou para a borda, ele é "preso pelo 42" e é tolerado.

    Returns:
        (lista dos becos de verdade, quantos são presos pelo 42)
    """
    real: list[Cell] = []
    enclosed = 0
    for x, y in cells:
        if bin(grid[y][x]).count("1") != 3:
            continue
        openable = any(grid[y][x] & WALL[letter]
                       and (x + dx, y + dy) in cells
                       for letter, (dx, dy) in STEP.items())
        if openable:
            real.append((x, y))
        else:
            enclosed += 1
    return real, enclosed


def walk(grid: Grid, start: Cell, letters: str) -> tuple[Cell, str]:
    """Anda pelas letras N/E/S/W. Devolve (onde parou, erro ou '')."""
    x, y = start
    for index, letter in enumerate(letters):
        if letter not in STEP:
            return (x, y), f"letra estranha '{letter}' na posição {index}"
        if grid[y][x] & WALL[letter]:
            return (x, y), (f"passo {index + 1} ('{letter}') atravessa "
                            f"uma parede em ({x},{y})")
        x, y = x + STEP[letter][0], y + STEP[letter][1]
    return (x, y), ""


# --------------------------------------------------------------------------
# Ajudantes para arquivos e para rodar o programa
# --------------------------------------------------------------------------

BASE_CONFIG = {
    "WIDTH": "20", "HEIGHT": "15", "ENTRY": "0,0", "EXIT": "19,14",
    "OUTPUT_FILE": "maze.txt", "PERFECT": "False", "SEED": "42",
}


def write_config(folder: Path, name: str,
                 changes: Optional[Mapping[str, Optional[str]]] = None,
                 extra: str = "") -> Path:
    """Escreve um config.txt de teste. ``None`` num valor apaga a chave."""
    values: dict[str, Optional[str]] = dict(BASE_CONFIG)
    values.update(changes or {})
    lines = [f"{key}={value}" for key, value in values.items()
             if value is not None]
    path = folder / name
    path.write_text("\n".join(lines) + "\n" + extra, encoding="utf-8")
    return path


def run_python(args: list[str], cwd: Path, stdin: str = "",
               timeout: int = 120) -> tuple[int, str]:
    """Roda ``python <args>``; devolve (código de saída, saída inteira)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, *args], input=stdin, capture_output=True,
            text=True, encoding="utf-8", errors="replace", cwd=cwd,
            env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -1, f"(travou: passou de {timeout}s sem terminar)"
    return proc.returncode, proc.stdout + proc.stderr


def run_program(args: list[str], cwd: Path,
                stdin: str = "") -> tuple[int, str]:
    """Roda o a_maze_ing.py de verdade, como o avaliador faria."""
    return run_python([str(ROOT / "a_maze_ing.py"), *args], cwd, stdin)


def has_traceback(output: str) -> bool:
    """True se o programa quebrou mostrando um traceback."""
    return "Traceback (most recent call last)" in output


@dataclass
class OutputFile:
    """O arquivo de saída, já lido e separado em partes."""

    grid: Grid
    entry: Cell
    exit: Cell
    path: str


def read_output(path: Path, width: int,
                height: int) -> tuple[Optional[OutputFile], list[str]]:
    """Lê o arquivo de saída e lista tudo que estiver fora do formato."""
    problems: list[str] = []
    raw = path.read_bytes()
    if b"\r" in raw:
        problems.append("tem \\r\\n (Windows); o subject pede só \\n")
    if not raw.endswith(b"\n"):
        problems.append("a última linha não termina com \\n")
    try:
        text = raw.decode("ascii").replace("\r", "")
    except UnicodeDecodeError:
        return None, problems + ["tem caracteres que não são ASCII"]
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != height + 4:
        problems.append(f"esperava {height + 4} linhas "
                        f"({height} da grade + 4), achei {len(lines)}")
        return None, problems
    grid: Grid = []
    for number, line in enumerate(lines[:height], start=1):
        if len(line) != width or not re.fullmatch(r"[0-9A-Fa-f]+", line):
            problems.append(f"linha {number} deveria ter {width} dígitos "
                            f"hexa, tem '{line[:30]}'")
            return None, problems
        grid.append([int(char, 16) for char in line])
    if lines[height] != "":
        problems.append("falta a linha vazia depois da grade")
    coords = []
    for label, line in (("entrada", lines[height + 1]),
                        ("saída", lines[height + 2])):
        match = re.fullmatch(r"(\d+),(\d+)", line)
        if not match:
            problems.append(f"linha da {label} deveria ser 'x,y': '{line}'")
            return None, problems
        coords.append((int(match.group(1)), int(match.group(2))))
    if not re.fullmatch(r"[NESW]*", lines[height + 3]):
        problems.append("o caminho só pode ter as letras N, E, S, W")
    return OutputFile(grid, coords[0], coords[1], lines[height + 3]), problems


def project_files() -> list[Path]:
    """Os .py escritos pela equipe (sem o analisador do subject)."""
    files = [ROOT / "a_maze_ing.py", ROOT / "config_reader.py",
             ROOT / "display.py", Path(__file__).resolve()]
    files += sorted((ROOT / "mazegen").glob("*.py"))
    return [path for path in files if path.exists()]


def has_module(name: str) -> bool:
    """True se o módulo está instalado (ex.: flake8, mypy)."""
    return importlib.util.find_spec(name) is not None


def grid_hash(grid: Grid) -> str:
    """Uma 'impressão digital' curta de uma grade."""
    text = "".join(f"{cell:X}" for row in grid for cell in row)
    return hashlib.sha1(text.encode()).hexdigest()[:10]


# --------------------------------------------------------------------------
# SALA 1 - A Papelada
# --------------------------------------------------------------------------

def room_paperwork(t: Tester) -> None:
    """Arquivos que o subject exige na raiz do repositório."""
    t.check("Python 3.10 ou mais novo", sys.version_info >= (3, 10),
            count=sys.version.split()[0])
    t.check("O programa principal se chama a_maze_ing.py",
            (ROOT / "a_maze_ing.py").exists())

    readme = ROOT / "README.md"
    if t.check("README.md existe", readme.exists(),
               hint="o README é obrigatório (capítulo VII)"):
        text = readme.read_text(encoding="utf-8")
        first = text.splitlines()[0] if text else ""
        pattern = (r"\*This project has been created as part of the 42 "
                   r"curriculum by .+\.\*")
        t.check("1ª linha do README em itálico, com os logins",
                re.fullmatch(pattern, first.strip()) is not None,
                detail=f"achei: {first[:60]}",
                hint="copie a frase exata do subject, entre *asteriscos*")
        t.check("Nenhum login de mentirinha (<login>) no README",
                "<login" not in text, bonus=True,
                detail="ainda tem um <loginN> para trocar",
                hint="troque pelo login de verdade da dupla")
        lower = text.lower()
        sections = {
            "Description": "## description", "Instructions":
            "## instructions", "Resources": "## resources",
        }
        missing = [name for name, tag in sections.items() if tag not in lower]
        t.check("Seções Description, Instructions e Resources",
                not missing, detail=f"faltando: {', '.join(missing)}")
        topics = {
            "formato do config": "config", "algoritmo": "algorithm",
            "por que o algoritmo": "why", "código reutilizável": "reusable",
            "papéis da equipe": "role", "uso de IA": " ai ",
        }
        missing = [name for name, word in topics.items() if word not in lower]
        t.check("Tópicos extras do capítulo VII (algoritmo, equipe, IA...)",
                not missing, detail=f"faltando: {', '.join(missing)}")

    license_file = ROOT / "LICENSE.md"
    if t.check("LICENSE.md existe", license_file.exists(),
               hint="o subject pede uma licença que permita reuso"):
        text = license_file.read_text(encoding="utf-8")
        known = ["MIT", "Apache", "BSD", "GPL", "MPL", "Unlicense", "ISC"]
        found = [name for name in known
                 if re.search(rf"\b{name}\b", text, re.IGNORECASE)]
        t.check("A licença tem nome conhecido", bool(found),
                count=", ".join(found))
        t.check("Nenhum login de mentirinha na LICENSE",
                "<login" not in text, bonus=True,
                detail="ainda tem um <loginN> no copyright")

    wheels = sorted(ROOT.glob("mazegen-*"))
    t.check("Pacote mazegen-* na raiz", bool(wheels),
            count=wheels[0].name if wheels else "",
            hint="rode: make package")
    t.check("pyproject.toml (para reconstruir o pacote)",
            (ROOT / "pyproject.toml").exists())

    makefile = ROOT / "Makefile"
    if t.check("Makefile existe", makefile.exists()):
        text = makefile.read_text(encoding="utf-8")
        rules = ["install", "run", "debug", "clean", "lint"]
        missing = [rule for rule in rules
                   if not re.search(rf"^{rule}\s*:", text, re.MULTILINE)]
        t.check("Regras install, run, debug, clean, lint", not missing,
                detail=f"faltando: {', '.join(missing)}")
        flags = [flag for flag in MANDATORY_MYPY_FLAGS if flag not in text]
        t.check("O lint usa as flags obrigatórias do mypy", not flags,
                detail=f"faltando: {', '.join(flags)}")
        t.check("Regra lint-strict (opcional, recomendada)",
                "lint-strict" in text, bonus=True)

    config = ROOT / "config.txt"
    if t.check("config.txt padrão existe", config.exists()):
        try:
            load_config(str(config))
            t.check("config.txt padrão é válido", True)
        except ValueError as error:
            t.check("config.txt padrão é válido", False, detail=str(error))
    t.check(".gitignore (não versionar lixo)",
            (ROOT / ".gitignore").exists(), bonus=True)


# --------------------------------------------------------------------------
# SALA 2 - O Porteiro (config_reader.py)
# --------------------------------------------------------------------------

BAD_CONFIGS: list[tuple[str, dict[str, Optional[str]], str]] = [
    ("falta a chave WIDTH", {"WIDTH": None}, ""),
    ("falta a chave OUTPUT_FILE", {"OUTPUT_FILE": None}, ""),
    ("falta a chave PERFECT", {"PERFECT": None}, ""),
    ("chave desconhecida (COLOR=blue)", {}, "COLOR=blue\n"),
    ("chave repetida (WIDTH duas vezes)", {}, "WIDTH=30\n"),
    ("linha sem '=' (WIDTH 20)", {}, "WIDTH 20\n"),
    ("valor vazio (HEIGHT=)", {"HEIGHT": ""}, ""),
    ("WIDTH=abc (não é número)", {"WIDTH": "abc"}, ""),
    ("WIDTH=1 (pequeno demais)", {"WIDTH": "1"}, ""),
    ("HEIGHT=101 (grande demais)", {"HEIGHT": "101"}, ""),
    ("WIDTH=-5 (negativo)", {"WIDTH": "-5"}, ""),
    ("ENTRY=1;2 (separador errado)", {"ENTRY": "1;2"}, ""),
    ("ENTRY=1,2,3 (coordenada a mais)", {"ENTRY": "1,2,3"}, ""),
    ("EXIT=a,b (não é número)", {"EXIT": "a,b"}, ""),
    ("PERFECT=maybe", {"PERFECT": "maybe"}, ""),
    ("SEED=xyz", {"SEED": "xyz"}, ""),
]


def room_config(t: Tester) -> None:
    """O leitor de configuração: aceita o certo, recusa o errado."""
    folder = t.workdir / "configs"
    folder.mkdir(exist_ok=True)

    def loads(path: Path) -> tuple[bool, str]:
        """Tenta ler o config: (aceitou?, mensagem de erro)."""
        try:
            load_config(str(path))
            return True, ""
        except ValueError as error:
            # Troca o caminho temporário enorme só pelo nome do arquivo.
            return False, str(error).replace(str(path), path.name)

    t.note("Primeiro, configs CERTOS (o porteiro tem que deixar entrar):")
    ok, error = loads(write_config(folder, "good.txt"))
    t.check("Config completo e correto", ok, detail=error)

    path = folder / "comments.txt"
    path.write_text("# um comentário\n\n" + write_config(
        folder, "tmp.txt").read_text(encoding="utf-8") + "\n# fim\n",
        encoding="utf-8")
    ok, error = loads(path)
    t.check("Comentários (#) e linhas vazias são ignorados", ok,
            detail=error)

    ok, error = loads(write_config(folder, "noseed.txt", {"SEED": None}))
    t.check("Sem SEED (ela é opcional)", ok, detail=error)

    path = folder / "lower.txt"
    path.write_text("width=20\nheight=15\nentry=0,0\nexit=19,14\n"
                    "output_file=maze.txt\nperfect=true\n", encoding="utf-8")
    ok, error = loads(path)
    t.check("Chaves minúsculas e PERFECT=true", ok, detail=error,
            bonus=True)

    path = folder / "spaces.txt"
    path.write_text("WIDTH = 20\nHEIGHT= 15\nENTRY =0, 0\nEXIT=19 ,14\n"
                    "OUTPUT_FILE=maze.txt\nPERFECT=False\n",
                    encoding="utf-8")
    ok, error = loads(path)
    t.check("Espaços em volta do '=' e da vírgula", ok, detail=error,
            bonus=True)

    try:
        config = load_config(str(write_config(folder, "values.txt")))
        right = (config.width, config.height, config.entry, config.exit,
                 config.output_file, config.perfect, config.seed) == (
            20, 15, (0, 0), (19, 14), "maze.txt", False, 42)
        t.check("Os valores lidos batem com o arquivo", right,
                detail=str(config))
    except ValueError as exc:
        t.check("Os valores lidos batem com o arquivo", False,
                detail=str(exc))

    t.note("Agora configs ERRADOS (o porteiro tem que barrar com uma "
           "mensagem clara):")
    for title, changes, extra in BAD_CONFIGS:
        ok, error = loads(write_config(folder, "bad.txt", changes, extra))
        t.check(f"Recusa: {title}", not ok,
                count=f"“{error[:28]}…”" if len(error) > 28
                else f"“{error}”",
                detail="foi aceito, mas deveria dar ValueError")

    ok, error = loads(folder / "nao_existe.txt")
    t.check("Recusa: arquivo que não existe", not ok,
            detail="deveria dar ValueError")
    path = folder / "binary.bin"
    path.write_bytes(bytes(range(128, 256)))
    ok, error = loads(path)
    t.check("Recusa: arquivo binário (não é texto)", not ok,
            detail="deveria dar ValueError")
    path = folder / "empty.txt"
    path.write_text("", encoding="utf-8")
    ok, error = loads(path)
    t.check("Recusa: arquivo vazio", not ok,
            detail="deveria dar ValueError")


# --------------------------------------------------------------------------
# SALA 3 - O Arquiteto (as regras do labirinto)
# --------------------------------------------------------------------------

def maze_cases(fast: bool) -> list[tuple[int, int, bool, int]]:
    """Os labirintos que vamos gerar: (largura, altura, perfeito, seed)."""
    sizes = [(20, 15), (9, 7), (10, 8), (31, 21), (50, 50), (5, 5), (4, 4),
             (2, 2), (100, 100)]
    seeds = [1, 42] if fast else [1, 2, 3, 42, 1337]
    if fast:
        sizes = sizes[:-1]
    cases = []
    for width, height in sizes:
        for seed in seeds:
            for perfect in (True, False):
                if (width, height) == (2, 2) and not perfect:
                    continue  # pequeno demais para o Pac-Man (testado à parte)
                cases.append((width, height, perfect, seed))
    return cases


def room_architect(t: Tester) -> None:
    """Gera muitos labirintos e confere cada regra do capítulo IV."""
    cases = maze_cases(t.fast)
    names = [
        "Gera sem erro",
        "Bordas externas todas fechadas",
        "Paredes coerentes entre vizinhas",
        "Conectado: toda célula fora do 42 é alcançável",
        "Nenhuma área aberta 3x3",
        "O 42 aparece (quando cabe) e é só célula fechada",
        "Entrada e saída fora do 42",
        "PERFECT=True → zero loops (um único caminho)",
        "PERFECT=False → pelo menos 2 loops",
        "PERFECT=False → 4 cantos e o centro livres",
        "PERFECT=False → no máximo 2 becos (fora os presos pelo 42)",
        "BÔNUS: PERFECT=False sem nenhum beco",
    ]
    tallies = {name: Tally() for name in names}
    enclosed_total = 0
    t.note(f"Vou gerar {len(cases)} labirintos de 2x2 até "
           f"{max(c[0] for c in cases)}x{max(c[1] for c in cases)}, "
           "nos dois modos, e conferir tudo com régua própria.")
    for index, (width, height, perfect, seed) in enumerate(cases, start=1):
        t.progress("labirintos", index, len(cases))
        label = f"{width}x{height} {'perfeito' if perfect else 'Pac-Man'} " \
                f"seed {seed}"
        maze = MazeGenerator(width, height, (0, 0), (width - 1, height - 1),
                             perfect=perfect, seed=seed)
        try:
            maze.generate()
        except ValueError as error:
            tallies["Gera sem erro"].add(str(error), label)
            continue
        tallies["Gera sem erro"].add(None, label)
        t.mazes.append((label, maze))
        grid, pattern = maze.grid, maze.pattern
        cells = free_cells(grid, pattern)
        reach = distances(grid, maze.entry)

        tallies["Bordas externas todas fechadas"].add(
            border_hole(grid), label)
        tallies["Paredes coerentes entre vizinhas"].add(
            incoherent_wall(grid), label)
        lost = [cell for cell in cells if cell not in reach]
        tallies["Conectado: toda célula fora do 42 é alcançável"].add(
            f"{len(lost)} células isoladas, ex.: {lost[0]}" if lost else None,
            label)
        square = open_3x3(grid)
        tallies["Nenhuma área aberta 3x3"].add(
            f"3x3 aberto começando em {square}" if square else None, label)

        problem = None
        if width >= 9 and height >= 7 and not pattern:
            problem = "o labirinto é grande o bastante, mas não tem o 42"
        elif any(grid[y][x] != CLOSED for x, y in pattern):
            problem = "uma célula do 42 tem parede aberta"
        tallies["O 42 aparece (quando cabe) e é só célula fechada"].add(
            problem, label)
        inside = maze.entry in pattern or maze.exit in pattern
        tallies["Entrada e saída fora do 42"].add(
            "entrada ou saída em cima do 42" if inside else None, label)

        loops = count_loops(grid, cells)
        if perfect:
            tallies["PERFECT=True → zero loops (um único caminho)"].add(
                f"{loops} loops" if loops else None, label)
            continue
        tallies["PERFECT=False → pelo menos 2 loops"].add(
            f"só {loops} loop(s)" if loops < 2 else None, label)
        key_cells = [(0, 0), (width - 1, 0), (0, height - 1),
                     (width - 1, height - 1), (width // 2, height // 2),
                     ((width - 1) // 2, (height - 1) // 2)]
        blocked = [cell for cell in key_cells if cell not in reach]
        tallies["PERFECT=False → 4 cantos e o centro livres"].add(
            f"célula {blocked[0]} não é corredor" if blocked else None,
            label)
        ends, trapped = dead_ends(grid, cells)
        enclosed_total += trapped
        tallies["PERFECT=False → no máximo 2 becos (fora os presos pelo 42)"
                ].add(
            f"{len(ends)} becos" if len(ends) > 2 else None, label)
        tallies["BÔNUS: PERFECT=False sem nenhum beco"].add(
            f"{len(ends)} beco(s), ex.: {ends[0]}" if ends else None, label)

    hints = {
        "Nenhuma área aberta 3x3": "veja _has_open_3x3_around no generator",
        "Paredes coerentes entre vizinhas":
            "abra/feche sempre as DUAS paredes (_open_wall)",
    }
    for name, tally in tallies.items():
        t.check(name, tally.ok, count=tally.score,
                detail=tally.first_problem, hint=hints.get(name, ""),
                bonus=name.startswith("BÔNUS"))

    if enclosed_total:
        t.note(f"{enclosed_total} beco(s) presos pelo 42 nos labirintos "
               "pequenos: não dá para abrir, e o analisador tolera.")
    t.note("Casos impossíveis têm que virar ValueError, nunca traceback:")
    impossible: list[tuple[str, Callable[[], object]]] = [
        ("2x2 no modo Pac-Man (não cabem 2 loops)",
         lambda: MazeGenerator(2, 2, perfect=False, seed=1).generate()),
        ("largura 1", lambda: MazeGenerator(1, 5)),
        ("entrada fora do labirinto", lambda: MazeGenerator(5, 5, (9, 9))),
        ("entrada = saída", lambda: MazeGenerator(5, 5, (1, 1), (1, 1))),
        ("entrada em cima do 42",
         lambda: MazeGenerator(20, 15, (5, 4), seed=1).generate()),
    ]
    for title, action in impossible:
        try:
            action()
            t.check(f"Recusa: {title}", False,
                    detail="foi aceito, mas deveria dar ValueError")
        except ValueError as error:
            t.check(f"Recusa: {title}", True, count=f"“{str(error)[:24]}…”")
        except Exception as error:  # noqa: BLE001 - queremos ver qualquer um
            t.check(f"Recusa: {title}", False,
                    detail=f"{type(error).__name__}: {error}")


# --------------------------------------------------------------------------
# SALA 4 - O Explorador (o caminho mais curto)
# --------------------------------------------------------------------------

def room_explorer(t: Tester) -> None:
    """Confere a solução: anda por ela e compara com um BFS próprio."""
    if not t.mazes:
        t.skip("Caminho mais curto", "a sala 3 não gerou labirintos")
        return
    extra: list[tuple[str, MazeGenerator]] = []
    for width, height in ((20, 15), (31, 21), (10, 8)):
        for perfect in (True, False):
            spots = [((0, height // 2), (width - 1, height // 2)),
                     ((width - 1, 0), (0, height - 1))]
            for entry, exit_ in spots:
                maze = MazeGenerator(width, height, entry, exit_,
                                     perfect=perfect, seed=7)
                try:
                    maze.generate()
                except ValueError:
                    continue
                extra.append((f"{width}x{height} {entry}→{exit_}", maze))
    every = t.mazes + extra
    t.note(f"{len(every)} labirintos: os da sala 3 e mais {len(extra)} com "
           "entrada e saída em lugares diferentes.")
    letters_ok, walks_ok, shortest = Tally(), Tally(), Tally()
    for label, maze in every:
        letters = maze.solution_letters()
        bad = set(letters) - set("NESW")
        letters_ok.add(f"letras estranhas: {bad}" if bad else None, label)
        end, error = walk(maze.grid, maze.entry, letters)
        if not error and end != maze.exit:
            error = f"o caminho termina em {end}, não na saída {maze.exit}"
        walks_ok.add(error or None, label)
        best = distances(maze.grid, maze.entry).get(maze.exit)
        shortest.add(None if best == len(letters) else
                     f"caminho com {len(letters)} passos, o menor tem {best}",
                     label)
    t.check("Só usa as letras N, E, S, W", letters_ok.ok,
            count=letters_ok.score, detail=letters_ok.first_problem)
    t.check("Vai da entrada até a saída sem atravessar parede", walks_ok.ok,
            count=walks_ok.score, detail=walks_ok.first_problem)
    t.check("É o caminho MAIS CURTO (comparado com BFS próprio)",
            shortest.ok, count=shortest.score,
            detail=shortest.first_problem,
            hint="o solve() precisa ser BFS (fila), não DFS (pilha)")
    sample = next(m for label, m in every if label.startswith("20x15"))
    letters = sample.solution_letters()
    t.note(f"Exemplo (20x15): {len(letters)} passos → "
           f"{letters[:40]}{'…' if len(letters) > 40 else ''}")


# --------------------------------------------------------------------------
# SALA 5 - A Semente
# --------------------------------------------------------------------------

def room_seed(t: Tester) -> None:
    """Mesma seed = mesmo labirinto. Seed diferente = labirinto diferente."""
    same = Tally()
    for seed in (1, 42, 2024):
        for perfect in (True, False):
            one = MazeGenerator(20, 15, perfect=perfect, seed=seed)
            two = MazeGenerator(20, 15, perfect=perfect, seed=seed)
            one.generate()
            two.generate()
            same.add(None if one.grid == two.grid else "grades diferentes",
                     f"seed {seed}")
    t.check("Mesma seed → labirinto idêntico", same.ok, count=same.score,
            detail=same.first_problem,
            hint="use random.Random(seed), nunca o random global")

    maze = MazeGenerator(20, 15, seed=99)
    first = [row[:] for row in maze.generate()]
    second = maze.generate()
    t.check("Chamar generate() duas vezes dá o mesmo resultado",
            first == second)

    prints: set[str] = set()
    for seed in range(10):
        maze = MazeGenerator(20, 15, seed=seed)
        maze.generate()
        prints.add(grid_hash(maze.grid))
    t.check("Seeds diferentes → labirintos diferentes", len(prints) >= 9,
            count=f"{len(prints)}/10 únicos")

    maze = MazeGenerator(20, 15)
    maze.generate()
    again = MazeGenerator(20, 15, seed=maze.seed)
    again.generate()
    t.check("Sem seed: sorteia uma e guarda (dá para repetir)",
            isinstance(maze.seed, int) and again.grid == maze.grid,
            count=f"seed {maze.seed}")


# --------------------------------------------------------------------------
# SALA 6 - O Programa de Verdade
# --------------------------------------------------------------------------

def room_program(t: Tester) -> None:
    """Roda o a_maze_ing.py como o avaliador faria."""
    folder = t.workdir / "program"
    folder.mkdir(exist_ok=True)
    output = folder / "maze.txt"

    t.note("Erros de uso: o programa tem que avisar e sair, nunca quebrar.")
    code, out = run_program([], folder)
    t.check("Sem argumentos → mostra como usar", code != 0 and
            "usage" in out.lower() and not has_traceback(out),
            count=f"saiu com {code}", detail=out[-200:])
    code, out = run_program(["a.txt", "b.txt"], folder)
    t.check("Argumentos demais → mostra como usar", code != 0 and
            not has_traceback(out), count=f"saiu com {code}",
            detail=out[-200:])
    code, out = run_program(["nao_existe.txt"], folder)
    t.check("Config que não existe → mensagem de erro", code != 0 and
            "error" in out.lower() and not has_traceback(out),
            count=f"saiu com {code}", detail=out[-200:])

    bad = [
        ("WIDTH=abc", {"WIDTH": "abc"}),
        ("ENTRY fora do labirinto", {"ENTRY": "50,50"}),
        ("ENTRY = EXIT", {"EXIT": "0,0"}),
        ("ENTRY em cima do 42", {"ENTRY": "5,4"}),
        ("pasta de saída que não existe",
         {"OUTPUT_FILE": "pasta/que/nao/existe/maze.txt"}),
        ("2x2 no modo Pac-Man", {"WIDTH": "2", "HEIGHT": "2",
                                 "EXIT": "1,1"}),
    ]
    clean = Tally()
    for title, changes in bad:
        config = write_config(folder, "bad.txt", changes)
        code, out = run_program([str(config)], folder, "4\n")
        problem = None
        if has_traceback(out):
            problem = "quebrou com traceback"
        elif code == 0 or "error" not in out.lower():
            problem = f"não mostrou 'Error' (saiu com {code})"
        clean.add(problem, title)
    t.check("Configs impossíveis → 'Error: ...' sem traceback", clean.ok,
            count=clean.score, detail=clean.first_problem)

    t.note("Agora uma rodada normal: gera, salva e sai pelo menu (4).")
    config = write_config(folder, "config.txt")
    t.wait("rodando python3 a_maze_ing.py config.txt")
    code, out = run_program([str(config)], folder, "4\n")
    t.check("Roda e sai com código 0", code == 0 and not has_traceback(out),
            count=f"saiu com {code}", detail=out[-300:])
    if not t.check("Cria o OUTPUT_FILE", output.exists()):
        return
    first_version = output.read_bytes()
    parsed, problems = read_output(output, 20, 15)
    t.check("Formato: 15 linhas de 20 dígitos hexa", parsed is not None,
            detail="\n".join(problems))
    t.check("Toda linha termina com \\n (sem \\r)",
            not any("\\n" in problem for problem in problems),
            detail="\n".join(problems))
    if parsed is None:
        return
    t.check("Linha vazia, depois entrada, saída e caminho", not problems,
            detail="\n".join(problems))
    t.check("Entrada e saída do arquivo = as do config",
            (parsed.entry, parsed.exit) == ((0, 0), (19, 14)),
            detail=f"achei {parsed.entry} e {parsed.exit}")
    grid = parsed.grid
    t.check("Paredes do arquivo: bordas fechadas e coerentes",
            border_hole(grid) is None and incoherent_wall(grid) is None,
            detail=f"{border_hole(grid)} / {incoherent_wall(grid)}")
    end, error = walk(grid, parsed.entry, parsed.path)
    best = distances(grid, parsed.entry).get(parsed.exit)
    t.check("Caminho do arquivo chega na saída e é o mais curto",
            not error and end == parsed.exit and best == len(parsed.path),
            count=f"{len(parsed.path)} passos",
            detail=error or f"terminou em {end}, menor = {best}")

    code, _ = run_program([str(config)], folder, "4\n")
    t.check("Mesma SEED no config → arquivo idêntico",
            output.read_bytes() == first_version)

    t.note("Testando o menu: 2 (caminho), 3 (cores), 1 (novo), 9 (inválido)"
           ", 4 (sair).")
    code, out = run_program([str(config)], folder, "2\n3\n1\n9\n4\n")
    t.check("Menu inteiro funciona e sai com 0",
            code == 0 and not has_traceback(out), detail=out[-300:])
    t.check("Opção 2 mostra o caminho (fundo ciano)", "\033[46m" in out)
    t.check("Opção 3 troca a cor das paredes", "walls: blue" in out,
            detail="esperava ver 'walls: blue' depois do 3")
    t.check("Opção 1 gera outro labirinto e reescreve o arquivo",
            output.read_bytes() != first_version)
    t.check("Opção inválida mostra um aviso", "invalid" in out.lower())
    code, out = run_program([str(config)], folder, "")
    t.check("Ctrl+D (fim da entrada) sai sem traceback",
            not has_traceback(out), count=f"saiu com {code}")

    small = write_config(folder, "small.txt",
                         {"WIDTH": "5", "HEIGHT": "5", "EXIT": "4,4"})
    code, out = run_program([str(small)], folder, "4\n")
    t.check("5x5 (o 42 não cabe) → avisa com mensagem de erro",
            "error" in out.lower() and "42" in out and code == 0,
            detail=out[-200:])

    perfect = write_config(folder, "perfect.txt", {"PERFECT": "True"})
    run_program([str(perfect)], folder, "4\n")
    parsed, _ = read_output(output, 20, 15)
    if parsed:
        closed = {(x, y) for y, row in enumerate(parsed.grid)
                  for x, cell in enumerate(row) if cell == CLOSED}
        loops = count_loops(parsed.grid, free_cells(parsed.grid, closed))
        t.check("PERFECT=True no config → arquivo sem nenhum loop",
                loops == 0, count=f"{loops} loops")


# --------------------------------------------------------------------------
# SALA 7 - O Analisador Oficial
# --------------------------------------------------------------------------

def verdict_of(report: str) -> str:
    """Pega a linha 'Verdict: ...' do relatório do analisador."""
    for line in report.splitlines():
        if line.startswith("Verdict:"):
            return line[len("Verdict:"):].strip()
    return report.strip().splitlines()[-1] if report.strip() else ""


def room_analyzer(t: Tester) -> None:
    """Passa os arquivos de saída pelo maze_analyzer.py do subject."""
    analyzer = ROOT / "maze_analyzer.py"
    if not analyzer.exists():
        t.skip("maze_analyzer.py", "não está na raiz: baixe dos anexos do "
               "projeto na intra e rode de novo")
        return
    from a_maze_ing import save_maze

    folder = t.workdir / "analyzer"
    folder.mkdir(exist_ok=True)
    sizes = [(20, 15), (9, 7), (30, 20)] if t.fast else \
        [(20, 15), (9, 7), (30, 20), (50, 50), (100, 100)]
    seeds = [1, 42] if t.fast else [1, 2, 3, 42]
    coherent, perfect_ok, pacman_ok, bonus = Tally(), Tally(), Tally(), \
        Tally()
    sample = ""
    jobs = [(w, h, s, p) for w, h in sizes for s in seeds
            for p in (True, False)]
    for index, (width, height, seed, perfect) in enumerate(jobs, start=1):
        t.progress("arquivos analisados", index, len(jobs))
        maze = MazeGenerator(width, height, perfect=perfect, seed=seed)
        maze.generate()
        path = folder / f"maze_{width}x{height}_{seed}_{perfect}.txt"
        save_maze(maze, str(path))
        code, report = run_python([str(analyzer), str(path)], folder)
        label = f"{width}x{height} seed {seed}"
        verdict = verdict_of(report)
        coherent.add(None if "Wall coherence   : OK" in report
                     else verdict, label)
        if perfect:
            perfect_ok.add(None if verdict.startswith("PERFECT") else verdict,
                           label)
            continue
        if (width, height, seed) == (20, 15, 42):
            sample = report
        pacman_ok.add(None if verdict.startswith("Pac-Man-USABLE")
                      else verdict, label)
        bonus.add(None if "bonus-grade" in verdict else verdict, label)
    t.check("Paredes coerentes (segundo o analisador)", coherent.ok,
            count=coherent.score, detail=coherent.first_problem)
    t.check("PERFECT=True → 'PERFECT maze'", perfect_ok.ok,
            count=perfect_ok.score, detail=perfect_ok.first_problem)
    t.check("PERFECT=False → 'Pac-Man-USABLE'", pacman_ok.ok,
            count=pacman_ok.score, detail=pacman_ok.first_problem)
    t.check("BÔNUS: 'bonus-grade' (zero becos)", bonus.ok, bonus=True,
            count=bonus.score, detail=bonus.first_problem)
    if sample:
        t.note("Relatório do analisador para o 20x15 seed 42 (Pac-Man):")
        for line in sample.strip().splitlines():
            print(t.paint(f"       │ {line}", "grey"))


# --------------------------------------------------------------------------
# SALA 8 - A Caixa de Presente (o pacote mazegen)
# --------------------------------------------------------------------------

def room_package(t: Tester) -> None:
    """O .whl: conteúdo, documentação, se instala e se está atualizado."""
    wheels = sorted(ROOT.glob("mazegen-*.whl")) + \
        sorted(ROOT.glob("mazegen-*.tar.gz"))
    if not t.check("Existe um mazegen-*.whl ou .tar.gz na raiz", bool(wheels),
                   hint="rode: make package"):
        return
    t.check("Só um pacote na raiz (sem versões velhas)", len(wheels) == 1,
            bonus=True, count=str(len(wheels)))
    wheel = wheels[0]
    if wheel.suffix != ".whl":
        t.skip("Conteúdo do pacote", "só sei abrir .whl")
        return
    try:
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            files = {name: archive.read(name) for name in names}
    except zipfile.BadZipFile:
        t.check("O .whl é um zip válido", False)
        return
    t.check("O .whl é um zip válido", True, count=f"{len(names)} arquivos")
    needed = ["mazegen/__init__.py", "mazegen/generator.py"]
    missing = [name for name in needed if name not in names]
    t.check("Tem o código (mazegen/__init__.py, generator.py)", not missing,
            detail=f"faltando: {missing}")
    metadata = next((files[n].decode("utf-8", "replace") for n in names
                     if n.endswith(".dist-info/METADATA")), "")
    metadata = metadata.replace("\r\n", "\n")
    t.check("Nome do pacote é 'mazegen'",
            re.search(r"^Name: mazegen$", metadata, re.MULTILINE) is not None)
    t.check("A documentação vai junto (README no pacote)",
            "mazegen/README.md" in names or "MazeGenerator" in metadata,
            hint="o subject pede código E documentação no pacote")
    t.check("A licença vai junto", any("LICENSE" in n for n in names),
            bonus=True)

    stale = []
    for source in sorted((ROOT / "mazegen").glob("*.py")):
        packed = files.get(f"mazegen/{source.name}")
        local = source.read_bytes().replace(b"\r\n", b"\n")
        if packed is None or packed.replace(b"\r\n", b"\n") != local:
            stale.append(source.name)
    t.check("O .whl está atualizado com o código", not stale,
            detail=f"diferente: {', '.join(stale)}",
            hint="mudou o generator? rode make package de novo")

    folder = t.workdir / "wheel_import"
    folder.mkdir(exist_ok=True)
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import mazegen; "
            "m = mazegen.MazeGenerator(20, 15, seed=42); m.generate(); "
            "print(mazegen.__file__); print(''.join(m.to_hex_lines()))")
    status, out = run_python(["-I", "-c", code, str(wheel)], folder)
    local_maze = MazeGenerator(20, 15, seed=42)
    local_maze.generate()
    lines = out.strip().splitlines()
    from_wheel = len(lines) == 2 and ".whl" in lines[0]
    t.check("Importa direto do .whl, num Python isolado", status == 0 and
            from_wheel, detail=out[-300:])
    t.check("O labirinto do .whl = o labirinto do código",
            from_wheel and lines[1] == "".join(local_maze.to_hex_lines()))

    if t.fast:
        t.skip("Reconstruir o pacote do zero", "modo --fast")
        return
    if not has_module("build"):
        t.skip("Reconstruir o pacote do zero",
               "instale com: pip install build (ou make install)")
        return
    build_dir = t.workdir / "build_src"
    shutil.copytree(ROOT / "mazegen", build_dir / "mazegen",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("pyproject.toml", "LICENSE.md", "README.md"):
        if (ROOT / name).exists():
            shutil.copy(ROOT / name, build_dir / name)
    t.wait("python -m build --wheel (como na defesa)")
    status, out = run_python(["-m", "build", "--wheel", "--outdir", "dist"],
                             build_dir, timeout=300)
    built = sorted((build_dir / "dist").glob("mazegen-*.whl"))
    t.check("Reconstrói o pacote a partir do código", status == 0 and
            bool(built), count=built[0].name if built else "",
            detail=out[-300:], bonus=True,
            hint="na defesa pedem para rodar o build num virtualenv")


# --------------------------------------------------------------------------
# SALA 9 - A Faxina (qualidade de código)
# --------------------------------------------------------------------------

def room_quality(t: Tester) -> None:
    """Docstrings, type hints, context managers, flake8, mypy e pytest."""
    no_doc: list[str] = []
    no_hint: list[str] = []
    raw_open: list[str] = []
    for path in project_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        with_calls = {id(item.context_expr) for node in ast.walk(tree)
                      if isinstance(node, ast.With) for item in node.items}
        for node in ast.walk(tree):
            where = f"{path.name}:{getattr(node, 'lineno', '?')}"
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                if ast.get_docstring(node) is None:
                    no_doc.append(f"{where} {node.name}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = node.args.posonlyargs + node.args.args + \
                    node.args.kwonlyargs
                args += [a for a in (node.args.vararg, node.args.kwarg) if a]
                bare = [a.arg for a in args if a.annotation is None
                        and a.arg not in ("self", "cls")]
                if bare or node.returns is None:
                    no_hint.append(f"{where} {node.name}")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)\
                    and node.func.id == "open" and id(node) not in with_calls:
                raw_open.append(where)
    files = ", ".join(path.name for path in project_files())
    t.note(f"Lendo o código de: {files}")
    t.check("Toda função e classe tem docstring", not no_doc,
            count=f"{len(no_doc)} sem", detail="\n".join(no_doc))
    t.check("Toda função tem type hints", not no_hint,
            count=f"{len(no_hint)} sem", detail="\n".join(no_hint))
    t.check("Todo open() está dentro de um 'with'", not raw_open,
            detail="\n".join(raw_open),
            hint="'with open(...)' fecha o arquivo sozinho")

    if t.fast:
        t.skip("flake8, mypy e pytest", "modo --fast")
        return
    tools: list[tuple[str, str, list[str], bool]] = [
        ("flake8 sem nenhum aviso", "flake8", ["-m", "flake8", "."], False),
        ("mypy com as flags obrigatórias", "mypy",
         ["-m", "mypy", ".", *MANDATORY_MYPY_FLAGS], False),
        ("mypy --strict (recomendado)", "mypy",
         ["-m", "mypy", ".", "--strict"], True),
        ("Testes do pytest (tests/test_maze.py)", "pytest",
         ["-m", "pytest", "-q", "-p", "no:cacheprovider",
          "tests/test_maze.py"], False),
    ]
    for title, module, command, bonus in tools:
        if not has_module(module):
            t.skip(title, f"instale com: pip install {module}")
            continue
        t.wait(f"rodando {module}")
        status, out = run_python(command, ROOT, timeout=300)
        found = re.search(r"\d+ passed|Found \d+ errors?", out)
        if found:
            summary = found.group(0)
        else:
            summary = "sem erros" if status == 0 else "com erros"
        t.check(title, status == 0, count=summary[:30], detail=out[-400:],
                bonus=bonus)


# --------------------------------------------------------------------------
# O passeio: banner, salas e placar
# --------------------------------------------------------------------------

ROOMS = [
    Room(1, "📜", "A Papelada",
         "Antes de entrar no labirinto, o porteiro confere os documentos: "
         "README, LICENSE, Makefile e o pacote. Sem eles a defesa nem "
         "começa.", room_paperwork),
    Room(2, "🔑", "O Porteiro (config_reader.py)",
         "O config.txt é o crachá. Vamos tentar entrar com crachás certos e "
         "com crachás falsificados: o porteiro tem que barrar cada um com "
         "uma mensagem clara, sem nunca desmaiar (traceback).", room_config),
    Room(3, "🧱", "O Arquiteto (as regras do labirinto)",
         "Hora de construir. Geramos dezenas de labirintos e medimos cada "
         "um com a nossa própria régua: bordas, paredes coerentes, "
         "conexão, nada de salão 3x3, o 42, os loops e os becos.",
         room_architect),
    Room(4, "🧭", "O Explorador (o caminho mais curto)",
         "Um explorador segue as letras N/E/S/W da solução, passo a passo. "
         "Ele não pode atravessar parede, tem que chegar na saída e não "
         "pode existir atalho mais curto.", room_explorer),
    Room(5, "🎲", "A Semente",
         "A seed é a receita do labirinto: a mesma receita tem que dar "
         "sempre o mesmo bolo, e receitas diferentes, bolos diferentes.",
         room_seed),
    Room(6, "🎮", "O Programa de Verdade",
         "Agora rodamos python3 a_maze_ing.py igualzinho ao avaliador: "
         "erros de uso, o arquivo de saída byte a byte e cada opção do "
         "menu.", room_program),
    Room(7, "🔬", "O Analisador Oficial",
         "O subject vem com um juiz: o maze_analyzer.py. Mandamos nossos "
         "arquivos para ele e lemos o veredito.", room_analyzer),
    Room(8, "📦", "A Caixa de Presente (o pacote mazegen)",
         "O gerador tem que ir embrulhado num .whl para outros projetos "
         "usarem. Abrimos a caixa, conferimos o conteúdo e instalamos num "
         "Python limpinho.", room_package),
    Room(9, "🧹", "A Faxina (qualidade de código)",
         "Por último, a vistoria: docstrings, type hints, arquivos fechados "
         "com 'with', flake8, mypy e os testes do pytest.", room_quality),
]


def banner(t: Tester) -> None:
    """O letreiro de abertura, com degradê e um Pac-Man comendo pontos."""
    word = "A-MAZE-ING"
    print()
    for row in range(5):
        line = " ".join(BIG_LETTERS[char][row] for char in word)
        if not t.color:
            print("   " + line)
            continue
        painted = "".join(
            f"\033[{GRADIENT[i * len(GRADIENT) // len(line)]}m{char}"
            for i, char in enumerate(line))
        print("   " + painted + "\033[0m")
    print()
    subtitle = "T  E  S  T  E  R   ·   uma visita guiada em 9 salas"
    print("   " + t.paint(subtitle, "bold", "white"))
    width = 60
    if t.animate:
        for step in range(width + 1):
            dots = "· " * ((width - step) // 2)
            mouth = "ᗧ" if step % 2 == 0 else "●"
            sys.stdout.write("\r   " + " " * step +
                             t.paint(mouth, "yellow", "bold") + " " +
                             t.paint(dots, "grey") + "\033[K")
            sys.stdout.flush()
            time.sleep(0.012)
        sys.stdout.write("\r\033[K")
    print("   " + t.paint("▚▞" * (width // 2), "magenta"))
    print()
    info = (f"   Python {sys.version.split()[0]} · pasta "
            f"{ROOT.name}/ · modo {'rápido' if t.fast else 'completo'}")
    print(t.paint(info, "grey"))
    print()


def room_header(t: Tester, room: Room, total: int) -> None:
    """O título de cada sala, com a historinha."""
    title = f" {room.icon}  SALA {room.number}/{total} · {room.title} "
    print()
    print(t.paint("━" * 3, "magenta") + t.paint(title, "bold", "white") +
          t.paint("━" * max(3, LINE_WIDTH - len(title)), "magenta"))
    for line in textwrap.wrap(room.story, LINE_WIDTH):
        sys.stdout.write("   ")
        t.type_out(t.paint(line, "italic", "cyan"))
    print()


def scoreboard(t: Tester, rooms: list[Room], elapsed: float) -> int:
    """O placar final. Devolve o código de saída (0 = tudo certo)."""
    print()
    print(t.paint("━" * (LINE_WIDTH + 14), "magenta"))
    print(t.paint("   🏁  PLACAR FINAL", "bold", "white"))
    print(t.paint("━" * (LINE_WIDTH + 14), "magenta"))
    passed = failed = warned = skipped = 0
    for room in rooms:
        ok, bad = room.count(PASS), room.count(FAIL)
        warn, skip = room.count(WARN), room.count(SKIP)
        passed, failed = passed + ok, failed + bad
        warned, skipped = warned + warn, skipped + skip
        total = ok + bad + warn
        size = 20
        filled = size * ok // total if total else size
        color = "red" if bad else ("yellow" if warn else "green")
        bar = t.paint("█" * filled, color) + t.paint("░" * (size - filled),
                                                     "grey")
        icon = ICONS[FAIL if bad else (WARN if warn else PASS)]
        title = f"{room.number}. {room.title.split(' (')[0]}"
        extras = []
        if warn:
            extras.append(t.paint(f"{warn}⚠", "yellow"))
        if skip:
            extras.append(t.paint(f"{skip}○", "grey"))
        print(f"   {room.icon}  {title:<28} {bar} "
              f"{t.paint(f'{ok:>3}/{total:<3}', color)} "
              f"{t.paint(icon[0], icon[1], 'bold')} {' '.join(extras)}")
    print()
    graded = passed + failed
    percent = 100 * passed // graded if graded else 100
    print(f"   {t.paint(f'{passed} passaram', 'green', 'bold')} · "
          f"{t.paint(f'{failed} falharam', 'red' if failed else 'grey')} · "
          f"{t.paint(f'{warned} avisos', 'yellow' if warned else 'grey')} · "
          f"{t.paint(f'{skipped} pulados', 'grey')} · "
          f"{elapsed:.1f}s")
    print()

    if failed:
        print(t.paint(f"   🔧  {percent}% — ainda tem parede no caminho. "
                      "O que consertar:", "bold", "red"))
        for room in rooms:
            for check in room.checks:
                if check.status == FAIL:
                    print(t.paint(f"      ✘ Sala {room.number}: "
                                  f"{check.name}", "red"))
                    if check.hint:
                        print(t.paint(f"        💡 {check.hint}", "yellow"))
        print()
        return 1

    trophy(t)
    message = "Tudo certo! O labirinto está pronto para a defesa."
    if warned:
        message += f" (Dá uma olhada nos {warned} avisos ⚠.)"
    print(t.paint(f"   🏆  {message}", "bold", "green"))
    print()
    return 0


def trophy(t: Tester) -> None:
    """Desenha um labirintinho resolvido como prêmio."""
    if not t.color:
        return
    from display import render

    maze = MazeGenerator(21, 9, perfect=False, seed=42)
    try:
        maze.generate()
    except ValueError:
        return
    for line in render(maze, True, 1).splitlines():
        print("   " + line)
    print()


def main() -> int:
    """Lê as opções, passeia pelas salas e mostra o placar."""
    parser = argparse.ArgumentParser(
        description="Tester do A-Maze-ing: uma visita guiada em 9 salas.")
    parser.add_argument("--fast", action="store_true",
                        help="menos labirintos, sem flake8/mypy/build")
    parser.add_argument("--no-color", action="store_true",
                        help="sem cores e sem animação")
    parser.add_argument("--only", type=int, nargs="+", metavar="N",
                        help="roda só estas salas (1 a 9)")
    args = parser.parse_args()

    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos e símbolos
    if os.name == "nt":
        # Truque conhecido: um comando vazio liga as cores ANSI no console
        # do Windows. A string é fixa, não há entrada do usuário aqui.
        os.system("")
    color = not args.no_color and sys.stdout.isatty() and \
        "NO_COLOR" not in os.environ
    t = Tester(color=color, animate=color, fast=args.fast)
    rooms = [room for room in ROOMS
             if not args.only or room.number in args.only]

    start = time.time()
    banner(t)
    try:
        for room in rooms:
            t.room = room
            room_header(t, room, len(ROOMS))
            try:
                room.run(t)
            except Exception as error:  # noqa: BLE001 - o tester não quebra
                t.record("A sala terminou sem erros inesperados", FAIL,
                         detail=f"{type(error).__name__}: {error}",
                         hint="isso pode ser bug do projeto OU do tester")
    except KeyboardInterrupt:
        print(t.paint("\n   Visita interrompida. Até a próxima!", "yellow"))
        return 130
    finally:
        shutil.rmtree(t.workdir, ignore_errors=True)
    return scoreboard(t, rooms, time.time() - start)


if __name__ == "__main__":
    sys.exit(main())
