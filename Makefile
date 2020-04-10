SHELL=bash
.PHONY: test

test:
	@source .bashrc && python setup.py test
