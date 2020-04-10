SHELL=bash
.PHONY: test

test:
	@-tput reset
	@source .bashrc && python setup.py test

install:
	@source .bashrc && python setup.py install
