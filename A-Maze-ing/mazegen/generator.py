"""O coração do projeto: a classe MazeGenerator.

Este arquivo NÃO sabe nada de config.txt, de terminal ou de cores.
Ele só sabe criar labirintos. Por isso pode ser reaproveitado em
qualquer outro projeto (é ele que vira o pacote pip "mazegen").

Como um labirinto é guardado
----------------------------
O labirinto é uma grade (lista de listas) de números inteiros.
``grid[y][x]`` é a célula da coluna ``x`` e da linha ``y``.
A célula (0, 0) é o canto de cima, à esquerda.

Cada número guarda as 4 paredes da célula, uma em cada bit::

    NORTH = 1  (bit 0)      EAST = 2  (bit 1)
    SOUTH = 4  (bit 2)      WEST = 8  (bit 3)

Exemplos: 9 = 1 + 8 -> paredes ao norte e a oeste.
          15 = 1 + 2 + 4 + 8 -> célula totalmente fechada.
"""

import random
from collections import deque
from typing import Optional

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST  # = 15

# Uma posição na grade: (x, y)
Cell = tuple[int, int]

# Uma direção: (passo em x, passo em y, minha parede, parede do vizinho,
# letra). Ex.: indo para o leste, eu abro a MINHA parede EAST e o vizinho
# abre a parede WEST dele - é a mesma parede, vista dos dois lados.
Direction = tuple[int, int, int, int, str]
DIRECTIONS: list[Direction] = [
    (0, -1, NORTH, SOUTH, "N"),
    (1, 0, EAST, WEST, "E"),
    (0, 1, SOUTH, NORTH, "S"),
    (-1, 0, WEST, EAST, "W"),
]

# O desenho do "42". "X" = célula fechada, "." = corredor normal.
# Primeiro tentamos a fonte grande. Se não couber, a pequena.
# Se nem a pequena couber, o 42 é omitido (labirinto pequeno demais).
# A fonte grande não tem "bolsos" de 1 célula de largura, então no
# modo Pac-Man ela não obriga nenhum beco sem saída.
FONT_BIG = {
    "4": ["X..X", "X..X", "X..X", "XXXX", "...X", "...X", "...X"],
    "2": ["XXXX", "...X", "...X", "XXXX", "X...", "X...", "XXXX"],
}
FONT_SMALL = {
    "4": ["X.X", "X.X", "XXX", "..X", "..X"],
    "2": ["XXX", "..X", "XXX", "X..", "XXX"],
}


class MazeGenerator:
    """Gera labirintos retangulares com um "42" desenhado no meio.

    Exemplo::

        from mazegen import MazeGenerator

        maze = MazeGenerator(20, 15, entry=(0, 0), exit_=(19, 14),
                             perfect=True, seed=42)
        maze.generate()
        print(maze.grid[0][0])          # paredes da célula (0, 0)
        print(maze.solve())             # [(0, 0), (1, 0), ...]
        print(maze.solution_letters())  # "ESSE..."

    Attributes:
        width: Número de colunas.
        height: Número de linhas.
        entry: Célula de entrada (x, y).
        exit: Célula de saída (x, y).
        perfect: True = um único caminho; False = tabuleiro Pac-Man.
        seed: Semente do sorteio. Mesma semente = mesmo labirinto.
        grid: A grade de paredes (vazia até chamar ``generate()``).
        pattern: Células fechadas que desenham o "42".
    """

    def __init__(self, width: int, height: int, entry: Cell = (0, 0),
                 exit_: Optional[Cell] = None, perfect: bool = False,
                 seed: Optional[int] = None) -> None:
        """Guarda e confere os parâmetros. Não gera nada ainda.

        Args:
            width: Largura em células (mínimo 2).
            height: Altura em células (mínimo 2).
            entry: Célula de entrada. Padrão: canto de cima à esquerda.
            exit_: Célula de saída. Padrão: canto de baixo à direita.
                (O "_" no nome é porque ``exit`` já existe no Python.)
            perfect: Se True, existe um único caminho entre 2 células.
            seed: Semente. Se None, uma é sorteada (veja ``self.seed``).

        Raises:
            ValueError: Se algum parâmetro for impossível.
        """
        if exit_ is None:
            exit_ = (width - 1, height - 1)
        if width < 2 or height < 2:
            raise ValueError("WIDTH and HEIGHT must be at least 2")
        for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(
                    f"{name} {x},{y} is outside the {width}x{height} maze")
        if entry == exit_:
            raise ValueError("ENTRY and EXIT must be different cells")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.perfect = perfect
        # Sem semente? Sorteamos uma e GUARDAMOS, para poder repetir depois.
        if seed is None:
            seed = random.randint(0, 999_999)
        self.seed: int = seed
        self.grid: list[list[int]] = []
        self.pattern: set[Cell] = set()
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Parte pública: o que outros projetos podem usar
    # ------------------------------------------------------------------

    def generate(self) -> list[list[int]]:
        """Cria o labirinto e devolve a grade.

        Passos:
            1. Começa com todas as paredes fechadas.
            2. Reserva as células do "42".
            3. Cava um labirinto perfeito (backtracking).
            4. Se ``perfect`` for False, abre paredes extras (Pac-Man).

        Returns:
            A grade ``grid[y][x]`` (também fica em ``self.grid``).

        Raises:
            ValueError: Se a entrada/saída cair no "42" ou se o
                labirinto for pequeno demais para o modo Pac-Man.
        """
        # Recria o sorteador: chamar generate() 2x dá o mesmo labirinto.
        self._rng = random.Random(self.seed)
        self.grid = [[ALL_WALLS] * self.width for _ in range(self.height)]
        self.pattern = self._find_42_cells()

        for name, cell in (("ENTRY", self.entry), ("EXIT", self.exit)):
            if cell in self.pattern:
                raise ValueError(
                    f"{name} {cell[0]},{cell[1]} falls on the '42' "
                    "pattern, please choose another cell")

        self._carve_perfect_maze()
        if not self.perfect:
            self._turn_into_pacman_board()
        return self.grid

    @property
    def has_pattern(self) -> bool:
        """True se o "42" coube no labirinto."""
        return len(self.pattern) > 0

    def has_wall(self, x: int, y: int, wall: int) -> bool:
        """Diz se a célula (x, y) tem a parede pedida (NORTH, EAST...)."""
        return self.grid[y][x] & wall != 0

    def is_free(self, x: int, y: int) -> bool:
        """True se (x, y) está dentro da grade e NÃO faz parte do 42."""
        inside = 0 <= x < self.width and 0 <= y < self.height
        return inside and (x, y) not in self.pattern

    def is_dead_end(self, x: int, y: int) -> bool:
        """True se a célula é um beco sem saída (3 paredes fechadas)."""
        # bin(13) = "0b1101" -> três "1" -> três paredes fechadas
        return self.is_free(x, y) and bin(self.grid[y][x]).count("1") == 3

    def count_dead_ends(self) -> int:
        """Quantos becos sem saída o labirinto tem."""
        return sum(1 for y in range(self.height) for x in range(self.width)
                   if self.is_dead_end(x, y))

    def count_loops(self) -> int:
        """Quantos caminhos alternativos (ciclos) o labirinto tem.

        Truque de grafos: um labirinto perfeito com C células tem
        exatamente C - 1 passagens abertas. Cada passagem a mais
        cria um ciclo novo. Labirinto perfeito -> 0 ciclos.
        """
        passages = 0
        free_cells = 0
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_free(x, y):
                    continue
                free_cells += 1
                # Contamos só leste e sul, senão cada passagem conta 2x.
                if not self.has_wall(x, y, EAST):
                    passages += 1
                if not self.has_wall(x, y, SOUTH):
                    passages += 1
        return passages - (free_cells - 1)

    def solve(self) -> list[Cell]:
        """Acha o MENOR caminho da entrada até a saída.

        Usa busca em largura (BFS): explora o labirinto "em ondas",
        primeiro tudo a 1 passo, depois tudo a 2 passos, etc.
        A primeira vez que a onda chega na saída é o menor caminho.

        Returns:
            Lista de células da entrada até a saída (ou [] se não houver).
        """
        self._check_generated()
        # came_from[célula] = de qual célula viemos para chegar nela
        came_from: dict[Cell, Optional[Cell]] = {self.entry: None}
        queue: deque[Cell] = deque([self.entry])
        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                break
            for dx, dy, wall, _, _ in DIRECTIONS:
                neighbour = (x + dx, y + dy)
                if self.has_wall(x, y, wall) or neighbour in came_from:
                    continue
                came_from[neighbour] = (x, y)
                queue.append(neighbour)

        if self.exit not in came_from:
            return []
        # Voltamos da saída até a entrada seguindo as "migalhas de pão".
        path: list[Cell] = []
        cell: Optional[Cell] = self.exit
        while cell is not None:
            path.append(cell)
            cell = came_from[cell]
        path.reverse()
        return path

    def solution_letters(self) -> str:
        """O menor caminho escrito com letras, ex.: "EESSWS"."""
        path = self.solve()
        letters = ""
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            for dx, dy, _, _, letter in DIRECTIONS:
                if (x2 - x1, y2 - y1) == (dx, dy):
                    letters += letter
        return letters

    def to_hex_lines(self) -> list[str]:
        """Cada linha da grade como texto, um dígito hexadecimal por célula.

        Ex.: a linha [9, 5, 3] vira "953"; [10, 12] vira "AC".
        """
        self._check_generated()
        return ["".join(f"{cell:X}" for cell in row) for row in self.grid]

    # ------------------------------------------------------------------
    # Parte interna (começa com "_"): detalhes de como o labirinto nasce
    # ------------------------------------------------------------------

    def _check_generated(self) -> None:
        """Reclama se alguém tentar usar o labirinto antes de gerá-lo."""
        if not self.grid:
            raise ValueError("call generate() before using the maze")

    def _find_42_cells(self) -> set[Cell]:
        """Calcula quais células formam o "42", centralizado na grade."""
        # Espaço entre o 4 e o 2: 1 coluna se a largura for ímpar, 2 se for
        # par. Assim o desenho fica centralizado E o centro do labirinto
        # cai nesse espaço (o centro precisa ficar livre no modo Pac-Man).
        gap = 1 if self.width % 2 == 1 else 2
        for font in (FONT_BIG, FONT_SMALL):
            rows = [four + "." * gap + two
                    for four, two in zip(font["4"], font["2"])]
            stamp_width = len(rows[0])
            stamp_height = len(rows)
            # Precisamos de pelo menos 1 célula livre em volta do desenho.
            if (self.width < stamp_width + 2
                    or self.height < stamp_height + 2):
                continue
            left = (self.width - stamp_width) // 2
            top = (self.height - stamp_height) // 2
            cells: set[Cell] = set()
            for dy, row in enumerate(rows):
                for dx, char in enumerate(row):
                    if char == "X":
                        cells.add((left + dx, top + dy))
            return cells
        return set()  # não coube nenhuma fonte

    def _open_wall(self, x: int, y: int, direction: Direction) -> None:
        """Abre a parede entre (x, y) e o vizinho, DOS DOIS LADOS."""
        dx, dy, wall, opposite, _ = direction
        self.grid[y][x] &= ~wall              # "&= ~" apaga o bit
        self.grid[y + dy][x + dx] &= ~opposite

    def _close_wall(self, x: int, y: int, direction: Direction) -> None:
        """Fecha a parede entre (x, y) e o vizinho, DOS DOIS LADOS."""
        dx, dy, wall, opposite, _ = direction
        self.grid[y][x] |= wall               # "|=" liga o bit
        self.grid[y + dy][x + dx] |= opposite

    def _carve_perfect_maze(self) -> None:
        """Cava o labirinto com o "backtracking recursivo" (usando pilha).

        Imagine um explorador com um rolo de barbante:
            1. Olha os vizinhos que ainda não visitou.
            2. Sorteia um, derruba a parede e anda até lá.
            3. Se não tem vizinho novo, volta um passo (pilha.pop()).
            4. Acaba quando voltou até o começo.
        Como nunca entra numa célula já visitada, não cria ciclos:
        o resultado é um labirinto perfeito.
        """
        visited: set[Cell] = {self.entry}
        stack: list[Cell] = [self.entry]
        while stack:
            x, y = stack[-1]
            options: list[Direction] = []
            for direction in DIRECTIONS:
                nx, ny = x + direction[0], y + direction[1]
                if self.is_free(nx, ny) and (nx, ny) not in visited:
                    options.append(direction)
            if not options:
                stack.pop()          # beco: volta pelo barbante
                continue
            direction = self._rng.choice(options)
            self._open_wall(x, y, direction)
            next_cell = (x + direction[0], y + direction[1])
            visited.add(next_cell)
            stack.append(next_cell)

    def _turn_into_pacman_board(self) -> None:
        """Transforma o labirinto perfeito num tabuleiro de Pac-Man.

        Abrir uma parede entre duas células já conectadas sempre cria
        UM ciclo novo e nunca cria um beco. Então:
            1. Cada beco sem saída ganha uma parede aberta (some o beco).
            2. Se ainda houver menos de 2 ciclos, abrimos mais paredes.
        """
        free_cells = [(x, y) for y in range(self.height)
                      for x in range(self.width) if self.is_free(x, y)]

        self._rng.shuffle(free_cells)
        for x, y in free_cells:
            if self.is_dead_end(x, y):
                self._open_random_wall(x, y)

        self._rng.shuffle(free_cells)
        for x, y in free_cells:
            if self.count_loops() >= 2:
                break
            self._open_random_wall(x, y)

        if self.count_loops() < 2:
            raise ValueError(
                "maze too small for PERFECT=False (it needs 2 loops): "
                "make it bigger or use PERFECT=True")

    def _open_random_wall(self, x: int, y: int) -> bool:
        """Tenta abrir uma parede de (x, y) que dê para outra célula livre.

        Nunca abre a borda nem o 42. Se abrir uma parede criar uma área
        aberta 3x3 (proibida), desfaz e tenta outra.

        Returns:
            True se conseguiu abrir alguma parede.
        """
        options = [d for d in DIRECTIONS
                   if self.has_wall(x, y, d[2])
                   and self.is_free(x + d[0], y + d[1])]
        self._rng.shuffle(options)
        for direction in options:
            self._open_wall(x, y, direction)
            if not self._has_open_3x3_around(x, y):
                return True
            self._close_wall(x, y, direction)  # desfaz
        return False

    def _has_open_3x3_around(self, x: int, y: int) -> bool:
        """Confere todos os quadrados 3x3 que contêm a célula (x, y)."""
        for top in range(y - 2, y + 1):
            for left in range(x - 2, x + 1):
                if self._is_open_3x3(left, top):
                    return True
        return False

    def _is_open_3x3(self, left: int, top: int) -> bool:
        """True se o quadrado 3x3 começando em (left, top) não tem
        nenhuma parede interna, ou seja, é uma "sala" grande demais."""
        if left < 0 or top < 0:
            return False
        if left + 3 > self.width or top + 3 > self.height:
            return False
        for y in range(top, top + 3):
            for x in range(left, left + 3):
                if x < left + 2 and self.has_wall(x, y, EAST):
                    return False
                if y < top + 2 and self.has_wall(x, y, SOUTH):
                    return False
        return True
