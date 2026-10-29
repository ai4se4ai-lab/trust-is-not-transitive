PYTHON ?= python
.PHONY: all smoke test formal paper verify-paper verify-results
all smoke test formal paper verify-paper verify-results:
	$(PYTHON) scripts/tasks.py $@
