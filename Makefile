# Makefile for setting up Python 3.13.4 and managing dependencies

# Default virtual environment directory
VENV_DIR := .venv

# Python version to install via pyenv
PYTHON_VERSION := 3.13.4

# Use pyenv's shim if available, otherwise fall back to system python
PY := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  brew       - Install Homebrew prerequisites (pyenv)"
	@echo "  pyenv      - Install Python $(PYTHON_VERSION) via pyenv"
	@echo "  venv       - Create virtual env with Python $(PYTHON_VERSION)"
	@echo "  install    - Install dependencies from requirements.txt"
	@echo "  upgrade    - Upgrade all deps to latest within constraints"
	@echo "  freeze     - Regenerate requirements.txt from current venv"
	@echo "  run        - Run the application UI"
	@echo "  clean      - Remove virtual env"

.PHONY: brew
brew:
	@command -v brew >/dev/null 2>&1 || { echo "Homebrew not found. Install from https://brew.sh"; exit 1; }
	brew update
	brew install pyenv || true
	@echo "Ensure pyenv is initialized in your shell (see 'pyenv init')."

.PHONY: pyenv
pyenv:
	@command -v pyenv >/dev/null 2>&1 || { echo "pyenv is not installed. Run 'make brew' first."; exit 1; }
	pyenv install -s $(PYTHON_VERSION)
	@echo "Python $(PYTHON_VERSION) installed via pyenv."

.PHONY: venv
venv:
	@command -v pyenv >/dev/null 2>&1 || { echo "pyenv is not installed. Run 'make brew' first."; exit 1; }
	@if [ ! -d $(VENV_DIR) ]; then \
		PYTHON_PATH=$$(pyenv prefix $(PYTHON_VERSION))/bin/python3 && \
		$$PYTHON_PATH -m venv $(VENV_DIR) && \
		$(VENV_DIR)/bin/python -m pip install --upgrade pip; \
		echo "Virtual environment created at $(VENV_DIR) using Python $(PYTHON_VERSION)."; \
	else \
		echo "Virtual environment already exists at $(VENV_DIR)."; \
	fi

.PHONY: install
install: venv
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		echo "requirements.txt not found. Run 'make freeze' after installing packages."; \
	fi

.PHONY: upgrade
upgrade: venv
	@if [ -f requirements.txt ]; then \
		$(PIP) install --upgrade -r requirements.txt; \
	else \
		echo "requirements.txt not found. Run 'make install' first."; \
	fi

.PHONY: freeze
freeze: venv
	$(PIP) freeze > requirements.txt
	@echo "requirements.txt updated from current environment."

.PHONY: run
run:
	$(PY) src/user_interface.py

.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	@echo "Removed $(VENV_DIR)."
