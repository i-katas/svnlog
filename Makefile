.PHONY: test
SHELL=bash
ACTIVATE_ENV=source .bashrc

test: check
	@-tput reset
	@${ACTIVATE_ENV} && python setup.py test

check:
	@${ACTIVATE_ENV} && flake8

install:
	@${ACTIVATE_ENV} && python setup.py install

clean:
	@rm -rf .pytest_cache .eggs build dist *.egg-info src/*.egg-info
	@find src test -name __pycache__ | xargs rm -rf
