*This project has been created as part of the 42 curriculum by hvaini-d, <login2>.*

# A-Maze-ing

## Descrição (Description)

O A-Maze-ing é um gerador de labirintos escrito em Python. Ele lê um arquivo
de configuração, gera um labirinto aleatório (mas reproduzível com uma seed),
salva o labirinto num arquivo usando uma codificação hexadecimal das paredes
e mostra tudo no terminal com um menu interativo.

Todo labirinto:

- tem parede em toda a borda externa, e as paredes entre células vizinhas
  são coerentes (as duas células concordam sobre a parede entre elas);
- é totalmente conectado (dá para chegar em qualquer célula), menos nas
  células do **"42"**, desenhado no meio com células totalmente fechadas;
- nunca tem uma área aberta de 3x3 células ou mais.

Existem dois modos:

| Modo | Config | Resultado |
|------|--------|-----------|
| Perfeito | `PERFECT=True` | exatamente um caminho entre quaisquer duas células (nenhum loop) |
| Pac-Man | `PERFECT=False` | um tabuleiro jogável: sem becos sem saída, vários loops, cantos e centro livres |

## Instruções (Instructions)

Requisito: Python 3.10 ou mais novo.

```bash
make install        # instala flake8, mypy, pytest e build
make run            # python3 a_maze_ing.py config.txt
make debug          # o mesmo, dentro do depurador pdb
make lint           # flake8 + mypy (flags obrigatórias)
make lint-strict    # flake8 + mypy --strict
make test           # testes unitários (pytest)
make tester         # visita guiada: confere cada regra do subject, explicando
make package        # gera o mazegen-1.0.0-py3-none-any.whl na raiz
make clean          # apaga os caches
```

Ou direto:

```bash
python3 a_maze_ing.py config.txt
```

Menu mostrado embaixo do labirinto:

```
1. Re-generate a new maze      (gera outro com uma seed nova e reescreve o arquivo)
2. Show / Hide the shortest path
3. Rotate the wall colours     (o "42" muda de cor junto)
4. Quit
```

Cores: entrada = magenta, saída = vermelho, caminho mais curto = ciano.

## Arquivo de configuração

Um `CHAVE=VALOR` por linha. Linhas que começam com `#` e linhas vazias são
ignoradas. Tanto faz escrever as chaves em maiúsculas ou minúsculas.

| Chave | Obrigatória | Descrição | Exemplo |
|-------|-------------|-----------|---------|
| `WIDTH` | sim | largura em células (de 2 a 100) | `WIDTH=20` |
| `HEIGHT` | sim | altura em células (de 2 a 100) | `HEIGHT=15` |
| `ENTRY` | sim | célula de entrada `x,y` | `ENTRY=0,0` |
| `EXIT` | sim | célula de saída `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | sim | onde salvar o labirinto | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | sim | `True` ou `False` | `PERFECT=False` |
| `SEED` | não | número inteiro: mesma seed = mesmo labirinto. Sem ela, uma é sorteada | `SEED=42` |

`(0,0)` é a célula do canto de cima à esquerda. A entrada e a saída precisam
ser diferentes, estar dentro do labirinto e fora do "42". Chave desconhecida,
chave repetida, chave faltando e valor inválido geram uma mensagem de erro
clara.

Se o labirinto for pequeno demais para o "42" (menor que 9x7), ele não é
desenhado e o programa mostra uma mensagem de erro.

### Arquivo de saída

Um dígito hexadecimal por célula, uma linha do arquivo por linha do
labirinto. Cada bit ligado é uma parede fechada: Norte = 1, Leste = 2,
Sul = 4, Oeste = 8. Depois vêm uma linha vazia, a entrada, a saída e o
caminho mais curto escrito com as letras `N`, `E`, `S`, `W`:

```
9515395...
...

0,0
19,14
SSEEESSSSSESWSSW...
```

## Algoritmo de geração

**Recursive backtracker** (busca em profundidade aleatória), escrito com uma
pilha em vez de recursão:

1. Começa com todas as paredes fechadas e marca as células do "42" como
   proibidas.
2. A partir da entrada, sorteia uma vizinha ainda não visitada, abre a
   parede entre as duas e anda até ela.
3. Quando não sobra vizinha não visitada, volta um passo (tira o topo da
   pilha).
4. Para quando a pilha esvazia: todas as células livres foram visitadas.

O resultado é um **labirinto perfeito** (uma árvore geradora). Para o modo
Pac-Man (`PERFECT=False`) o labirinto é "trançado" (*braided*) depois: cada
beco sem saída ganha uma parede a mais aberta, o que sempre cria um loop e
nunca cria um beco novo. Uma abertura é recusada se fosse criar uma área
aberta 3x3. Se ficarem menos de 2 loops, mais paredes são abertas.

O caminho mais curto é encontrado com uma **busca em largura** (BFS).

### Por que este algoritmo

- É curto e fácil de explicar: "anda ao acaso e volta quando fica preso".
- Gera corredores longos e sinuosos, que ficam bonitos.
- Desviar do "42" é trivial: basta marcar essas células como já visitadas.
- Sempre gera um labirinto perfeito, e trançar um labirinto perfeito é um
  jeito simples de chegar no tabuleiro do Pac-Man.

## Código reutilizável

O gerador inteiro fica no pacote `mazegen/`, numa única classe,
`MazeGenerator`, que não sabe nada sobre o arquivo de configuração nem sobre
o terminal. Ele é empacotado como `mazegen-1.0.0-py3-none-any.whl` (na raiz
do repositório) e pode ser reconstruído com `make package` (precisa de
`pip install build`).

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

```python
from mazegen import MazeGenerator, EAST

# Uso básico
maze = MazeGenerator(20, 15)          # seed sorteada, modo Pac-Man
maze.generate()

# Parâmetros personalizados
maze = MazeGenerator(width=30, height=20, entry=(0, 0), exit_=(29, 19),
                     perfect=True, seed=42)
maze.generate()

# Acessar a estrutura
maze.grid[y][x]                       # int de 0 a 15, bits N=1 E=2 S=4 W=8
maze.has_wall(3, 2, EAST)             # True / False
maze.pattern                          # conjunto de células (x, y) do "42"

# Acessar uma solução
maze.solve()                          # [(0, 0), (1, 0), ...]
maze.solution_letters()               # "ESSE..."
```

`config_reader.py`, `display.py` e `a_maze_ing.py` são específicos deste
projeto e não fazem parte do pacote.

## Estrutura do projeto

```
a_maze_ing.py      programa principal: config -> labirinto -> arquivo -> menu
config_reader.py   lê e confere o arquivo de configuração
display.py         desenha o labirinto no terminal (cores ANSI)
mazegen/           o pacote reutilizável (MazeGenerator)
tests/             testes unitários (pytest) + tester.py (tester guiado no terminal)
```

## Equipe e gestão do projeto

- **Papéis**:
  - hvaini-d: geração do labirinto, empacotamento, testes.
  - <login2>: leitor de configuração, exibição no terminal, README.
- **Planejamento**: primeiro um protótipo num arquivo só; depois o código foi
  dividido em módulos pequenos, para que cada parte pudesse ser estudada
  separadamente. O modo Pac-Man entrou quando o subject foi atualizado
  (v2.3).
- **O que funcionou bem**: escrever um teste para cada regra do subject
  facilitou conferir que nenhuma mudança deixava o labirinto inválido.
- **O que poderia melhorar**: uma tela gráfica com a MLX, mais de um
  algoritmo de geração, animação durante a geração.
- **Ferramentas**: VS Code, git, flake8, mypy, pytest, Claude Code.

## Recursos (Resources)

- [Maze generation algorithm - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Jamis Buck - Maze algorithms](https://weblog.jamisbuck.com/2011/2/7/maze-generation-algorithm-recap)
- [Breadth-first search - Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Braid mazes (Think Labyrinth)](https://www.astrolog.org/labyrnth/algrithm.htm)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [Choose a license](https://choosealicense.com/licenses/mit/)

### Como a IA foi usada

O Claude Code foi usado para:

- reorganizar o código em módulos pequenos e comentados;
- revisar o projeto contra o subject, regra por regra;
- escrever os testes unitários, o tester guiado e os arquivos de
  empacotamento (pyproject.toml, Makefile);
- criar um material de estudo usado pela equipe para aprender o projeto.

Cada parte foi lida, executada e discutida pela equipe antes de ser mantida.
