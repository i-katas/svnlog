SHELL=bash
.PHONY: test

test:
	@-tput reset
	@source .bashrc && python setup.py test

install:
	@source .bashrc && python setup.py install

clean:
	@rm -rf .pytest_cache .eggs build dist *.egg-info src/*.egg-info
	@find src test -name __pycache__ | xargs rm -rf
