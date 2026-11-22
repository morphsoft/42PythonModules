"""Desenha o labirinto no terminal, com cores.

A ideia: cada célula vira um quadradinho de 2 espaços coloridos.
Entre duas células sempre existe um "espaço de parede", que pinta
como parede (fechada) ou deixa vazio (aberta). Então uma grade de
3x2 células vira um desenho de 7x5 quadradinhos::

    # # # # # # #        # = parede / quina
    # c . c . c #        c = célula
    # # # . # # #        . = lugar de parede (aberta ou fechada)
    # c . c . c #
    # # # # # # #

A célula (x, y) fica na posição (2x + 1, 2y + 1) do desenho.
"""

from mazegen import EAST, NORTH, SOUTH, WEST, MazeGenerator

# Códigos ANSI: "\033[XXm" muda a cor de FUNDO; RESET volta ao normal.
RESET = "\033[0m"
ENTRY_COLOR = "\033[45m"   # magenta
EXIT_COLOR = "\033[41m"    # vermelho
PATH_COLOR = "\033[46m"    # ciano

# Temas de cor: (nome, cor das paredes, cor do "42").
# A opção "trocar cores" do menu só passa para o próximo da lista.
THEMES = [
    ("white", "\033[107m", "\033[100m"),
    ("blue", "\033[44m", "\033[104m"),
    ("green", "\033[42m", "\033[102m"),
    ("yellow", "\033[43m", "\033[103m"),
]

EMPTY = "  "


def block(color: str) -> str:
    """Um quadradinho colorido (2 espaços com fundo colorido)."""
    return color + "  " + RESET


def render(maze: MazeGenerator, show_path: bool, theme: int) -> str:
    """Monta o desenho do labirinto como um texto pronto para print().

    Args:
        maze: Um labirinto já gerado.
        show_path: Se True, pinta o menor caminho.
        theme: Índice na lista THEMES.

    Returns:
        O desenho, com uma linha de texto por linha do desenho.
    """
    _, wall_color, pattern_color = THEMES[theme]
    wall = block(wall_color)

    # 1) Começa com TUDO parede.
    canvas = [[wall] * (2 * maze.width + 1)
              for _ in range(2 * maze.height + 1)]

    # 2) Esvazia cada célula e cada parede aberta.
    for y in range(maze.height):
        for x in range(maze.width):
            cx, cy = 2 * x + 1, 2 * y + 1
            if (x, y) in maze.pattern:
                canvas[cy][cx] = block(pattern_color)
                continue
            canvas[cy][cx] = EMPTY
            if not maze.has_wall(x, y, NORTH):
                canvas[cy - 1][cx] = EMPTY
            if not maze.has_wall(x, y, SOUTH):
                canvas[cy + 1][cx] = EMPTY
            if not maze.has_wall(x, y, WEST):
                canvas[cy][cx - 1] = EMPTY
            if not maze.has_wall(x, y, EAST):
                canvas[cy][cx + 1] = EMPTY

    # 3) Pinta o caminho: as células E o espaço entre duas seguidas.
    if show_path:
        path = maze.solve()
        for x, y in path:
            canvas[2 * y + 1][2 * x + 1] = block(PATH_COLOR)
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            # O meio entre (2x1+1) e (2x2+1) é x1 + x2 + 1.
            canvas[y1 + y2 + 1][x1 + x2 + 1] = block(PATH_COLOR)

    # 4) Entrada e saída por último, para ficarem por cima de tudo.
    ex, ey = maze.entry
    canvas[2 * ey + 1][2 * ex + 1] = block(ENTRY_COLOR)
    sx, sy = maze.exit
    canvas[2 * sy + 1][2 * sx + 1] = block(EXIT_COLOR)

    return "\n".join("".join(row) for row in canvas)
