SHELL=bash
.PHONY: test

test: check
	@-tput reset
	@source .bashrc && python setup.py test

check:
	@flake8

install:
	@source .bashrc && python setup.py install

clean:
	@rm -rf .pytest_cache .eggs build dist *.egg-info src/*.egg-info
	@find src test -name __pycache__ | xargs rm -rf
