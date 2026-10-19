PYTHON ?= python3
NODE ?= node

.PHONY: help check verify bundle validate-native

help:
	@printf '%s\n' 'make check' 'make verify' 'make bundle' 'make validate-native'

check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v
	$(NODE) --test tests/model.test.cjs

verify: check bundle

bundle:
	$(PYTHON) scripts/bundle.py

validate-native:
	omarchy plugin validate .
