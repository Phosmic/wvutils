PYTHON=python3

install:
	${PYTHON} -m pip install .

install-dev:
	${PYTHON} -m pip install -e .

test:
	${PYTHON} -m pytest tests

build:
	${PYTHON} -m build

publish:
	${PYTHON} -m build
	twine upload dist/wvutils-*.tar.gz dist/wvutils-*.whl
