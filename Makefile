.PHONY: test
SHELL=bash
ACTIVATE_ENV=source .bashrc

test: check
	@${ACTIVATE_ENV} && python setup.py test

check:
	@-tput reset
	@${ACTIVATE_ENV} && flake8

install:
	@${ACTIVATE_ENV} && pip install .

uninstall:
	@${ACTIVATE_ENV} && pip uninstall svnlog -y

clean:
	@rm -rf .pytest_cache .eggs build dist *.egg-info svnlog/*.egg-info .coverage
	@find svnlog test -name __pycache__ -o -name *.egg-info | xargs rm -rf
