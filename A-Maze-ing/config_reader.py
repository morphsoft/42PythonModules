"""Lê e confere o arquivo de configuração (ex.: config.txt).

Formato: uma linha ``CHAVE=VALOR`` por linha. Linhas que começam com
``#`` são comentários e são ignoradas. Linhas vazias também.

Exemplo::

    WIDTH=20
    HEIGHT=15
    ENTRY=0,0
    EXIT=19,14
    OUTPUT_FILE=maze.txt
    PERFECT=False
    SEED=42

SEED é opcional; todas as outras chaves são obrigatórias.
"""

from dataclasses import dataclass
from typing import Optional

REQUIRED_KEYS = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                 "PERFECT"]
OPTIONAL_KEYS = ["SEED"]
# Acima disso o desenho não cabe numa tela de terminal.
MAX_SIZE = 100


@dataclass
class MazeConfig:
    """Todas as opções do config.txt, já convertidas para o tipo certo.

    Um ``@dataclass`` é só uma classe que guarda dados: o Python cria
    o ``__init__`` sozinho a partir da lista de campos abaixo.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def load_config(path: str) -> MazeConfig:
    """Lê o arquivo, confere tudo e devolve um MazeConfig.

    Args:
        path: Caminho do arquivo de configuração.

    Returns:
        A configuração pronta para uso.

    Raises:
        ValueError: Com uma mensagem clara se algo estiver errado.
    """
    values = read_key_values(path)

    for key in REQUIRED_KEYS:
        if key not in values:
            raise ValueError(f"missing mandatory key '{key}' in {path}")

    config = MazeConfig(
        width=parse_int(values["WIDTH"], "WIDTH"),
        height=parse_int(values["HEIGHT"], "HEIGHT"),
        entry=parse_coordinates(values["ENTRY"], "ENTRY"),
        exit=parse_coordinates(values["EXIT"], "EXIT"),
        output_file=values["OUTPUT_FILE"],
        perfect=parse_bool(values["PERFECT"], "PERFECT"),
    )
    if "SEED" in values:
        config.seed = parse_int(values["SEED"], "SEED")

    for name, size in (("WIDTH", config.width), ("HEIGHT", config.height)):
        if not 2 <= size <= MAX_SIZE:
            raise ValueError(
                f"{name} must be between 2 and {MAX_SIZE}, got {size}")
    return config


def read_key_values(path: str) -> dict[str, str]:
    """Lê o arquivo e devolve um dicionário {"WIDTH": "20", ...}.

    Os valores ainda são textos; a conversão vem depois.
    """
    try:
        # "with" fecha o arquivo sozinho, mesmo se der erro no meio.
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise ValueError(f"config file '{path}' not found")
    except UnicodeDecodeError:
        raise ValueError(f"config file '{path}' is not a text file")
    except OSError as error:
        raise ValueError(f"cannot read '{path}': {error.strerror}")

    values: dict[str, str] = {}
    for number, line in enumerate(lines, start=1):
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(
                f"{path} line {number}: expected KEY=VALUE, got '{line}'")
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()
        if key not in REQUIRED_KEYS + OPTIONAL_KEYS:
            raise ValueError(f"{path} line {number}: unknown key '{key}'")
        if key in values:
            raise ValueError(f"{path} line {number}: '{key}' appears twice")
        if value == "":
            raise ValueError(f"{path} line {number}: '{key}' has no value")
        values[key] = value
    return values


def parse_int(text: str, key: str) -> int:
    """Converte "20" em 20, ou dá um erro claro."""
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{key} must be an integer, got '{text}'")


def parse_coordinates(text: str, key: str) -> tuple[int, int]:
    """Converte "3,7" em (3, 7), ou dá um erro claro."""
    parts = text.split(",")
    if len(parts) != 2:
        raise ValueError(f"{key} must look like x,y (e.g. 0,0), "
                         f"got '{text}'")
    return (parse_int(parts[0].strip(), key),
            parse_int(parts[1].strip(), key))


def parse_bool(text: str, key: str) -> bool:
    """Converte "True"/"False" (maiúsculas ou minúsculas) em bool."""
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    raise ValueError(f"{key} must be True or False, got '{text}'")
