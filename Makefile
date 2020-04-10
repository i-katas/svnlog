SHELL=bash
.PHONY: test

test:
	@source .bashrc && python setup.py test

install:
	@source .bashrc && python setup.py install
