SOURCE_DIR ?= .
TESTS_DIR ?= tests
PYTHON ?= python3
POETRY ?= poetry
VENV ?= .venv/bin/activate

# Based on https://tech.davis-hansson.com/p/make/
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

# # On Linux and macOS, 'which' can help us find python3.
# # On Windows (with MinGW/MSYS), 'where' is the equivalent.
# ifeq ($(OS),Windows_NT)
#   FIND_CMD := where
#   REDIRECT := 2> nul
# else
#   FIND_CMD := which
#   REDIRECT := 2> /dev/null
# endif

# # Locate the python3 executable using system tools.
# DETECTED_PYTHON3 := $(shell $(FIND_CMD) python3 $(REDIRECT))

.PHONY: help
help:  ## print help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: install-deps  ## install dependencies
install-deps:
	$(POETRY) install --no-interaction --no-root
	$(POETRY) show

.PHONY: update-deps  ## update requirements.txt file from poetry
update-deps:
	$(POETRY) update
	$(POETRY) export \
		--format requirements.txt \
		--output requirements.txt \
		--without-hashes

.PHONY:

requirements.txt: poetry.lock
	$(POETRY) export \
		--format requirements.txt \
		--output requirements.txt \
		--without-hashes

requirements.dev.txt: poetry.lock
	$(POETRY) export \
		--with dev \
		--format requirements.txt \
		--output requirements.dev.txt \
		--without-hashes

.PHONY: check-generated-requirements
check-generated-requirements:
	. $(VENV)
	tmpdir=$$(mktemp -d)
	trap 'rm -rf "$${tmpdir}"' EXIT
	$(POETRY) export \
		--format requirements.txt \
		--output "$${tmpdir}/requirements.txt" \
		--without-hashes
	$(POETRY) export \
		--with dev \
		--format requirements.txt \
		--output "$${tmpdir}/requirements.dev.txt" \
		--without-hashes
	diff --unified=0 requirements.txt "$${tmpdir}/requirements.txt"
	diff --unified=0 requirements.dev.txt "$${tmpdir}/requirements.dev.txt"

.PHONY: format
format:  ## automatically format code to standards
	. $(VENV)
	ruff check --fix .
	isort .
	black $(SOURCE_DIR) $(TESTS_DIR)

.PHONY: lint
lint:  ## lint code against standards
	. $(VENV)
	ruff check .
	isort . --check --diff
	black $(SOURCE_DIR) $(TESTS_DIR) --diff
	mypy $(SOURCE_DIR)

.PHONY: test tests
tests: test
test:  ## execute unit tests
	. $(VENV)
	pytest $(TESTS_DIR) --cov $(SOURCE_DIR)
