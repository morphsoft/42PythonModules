"""A-Maze-ing - programa principal.

Uso:
    python3 a_maze_ing.py config.txt

O que acontece, em ordem:
    1. Lê o arquivo de configuração   (config_reader.py)
    2. Gera o labirinto                (mazegen/generator.py)
    3. Salva no OUTPUT_FILE            (save_maze, aqui embaixo)
    4. Mostra no terminal + menu       (display.py)
"""

import sys
from typing import Optional

from config_reader import MazeConfig, load_config
from display import THEMES, render
from mazegen import MazeGenerator

CLEAR_SCREEN = "\033[2J\033[H"
MENU = """=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit"""


def create_maze(config: MazeConfig, seed: Optional[int]) -> MazeGenerator:
    """Gera um labirinto com as opções do config e já salva no arquivo.

    Args:
        config: A configuração lida do arquivo.
        seed: Semente a usar. None = sorteia uma nova.

    Returns:
        O labirinto gerado.
    """
    maze = MazeGenerator(config.width, config.height, config.entry,
                         config.exit, config.perfect, seed)
    maze.generate()
    save_maze(maze, config.output_file)
    return maze


def save_maze(maze: MazeGenerator, filename: str) -> None:
    """Escreve o arquivo de saída no formato pedido pelo subject.

    Formato:
        - uma linha por linha da grade, um dígito hexa por célula
        - uma linha vazia
        - a entrada "x,y", a saída "x,y" e o caminho em letras (N/E/S/W)
    """
    lines = maze.to_hex_lines()
    lines.append("")
    lines.append(f"{maze.entry[0]},{maze.entry[1]}")
    lines.append(f"{maze.exit[0]},{maze.exit[1]}")
    lines.append(maze.solution_letters())
    try:
        # newline="\n": toda linha termina com \n, até no Windows.
        with open(filename, "w", encoding="utf-8", newline="\n") as file:
            for line in lines:
                file.write(line + "\n")
    except OSError as error:
        raise ValueError(f"cannot write '{filename}': {error.strerror}")


def show_screen(maze: MazeGenerator, show_path: bool, theme: int,
                message: str) -> None:
    """Limpa a tela e desenha: labirinto, informações e menu."""
    print(CLEAR_SCREEN, end="")
    print(render(maze, show_path, theme))
    if not maze.has_pattern:
        print("Error: the maze is too small to draw the '42' pattern.")
    mode = "perfect" if maze.perfect else "Pac-Man"
    print(f"{maze.width}x{maze.height} | {mode} mode | seed {maze.seed}"
          f" | walls: {THEMES[theme][0]}")
    print(MENU)
    if message:
        print(message)


def run_menu(config: MazeConfig, maze: MazeGenerator) -> None:
    """O loop do menu: mostra a tela, lê a escolha, repete."""
    show_path = False
    theme = 0
    message = ""
    while True:
        show_screen(maze, show_path, theme, message)
        message = ""
        choice = input("Choice? (1-4): ").strip()
        if choice == "1":
            try:
                maze = create_maze(config, seed=None)
            except ValueError as error:
                message = f"Error: {error}"
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            theme = (theme + 1) % len(THEMES)
        elif choice == "4":
            print("Bye!")
            return
        else:
            message = f"Invalid choice '{choice}', type 1, 2, 3 or 4."


def main() -> int:
    """Ponto de entrada. Devolve 0 se deu tudo certo, 1 se deu erro."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        return 1
    try:
        config = load_config(sys.argv[1])
        maze = create_maze(config, config.seed)
        print(f"Maze written to {config.output_file}")
        run_menu(config, maze)
    except ValueError as error:
        # Todos os nossos erros "esperados" viram ValueError com mensagem.
        print(f"Error: {error}")
        return 1
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou Ctrl+D: sai sem mostrar traceback.
        print("\nBye!")
    except Exception as error:
        # Rede de segurança: o programa NUNCA pode quebrar com traceback.
        print(f"Unexpected error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
