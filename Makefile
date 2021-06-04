.PHONY: clean-pyc clean-tests clean docs

all: clean-pyc clean-tests clean test

clean-all: clean-pyc clean-tests clean

test:
	tox -e py3-unit

clean:
	rm -rf *.egg
	rm -rf *.egg-info
	rm -rf .cache
	rm -rf .tox
	rm -rf build
	rm -rf dist

clean-tests:
	rm -rf tests/.coverage*
	rm -rf tests/.cache
	rm -rf tests/coverage
	rm -rf tests/__pycache__
	rm -rf .tox

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

bump-major:
	bumpversion major --commit

bump-minor:
	bumpversion minor --commit

bump-patch:
	bumpversion patch --commit