PYTHON  = python3
CONFIG  = config.txt
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test package

# Instala as ferramentas de desenvolvimento.
install:
	$(PYTHON) -m pip install flake8 mypy pytest build

# Roda o programa.
run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

# Roda dentro do depurador pdb (n = próxima linha, c = continuar, q = sair).
debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

# Apaga caches e arquivos temporários (o .whl na raiz fica!).
clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache build dist *.egg-info

lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 .
	mypy . --strict

test:
	$(PYTHON) -m pytest tests

# Gera o pacote mazegen-1.0.0-py3-none-any.whl na raiz do repositório.
package:
	$(PYTHON) -m build --wheel
	cp dist/mazegen-*.whl .
