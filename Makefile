# Makefile for TinyEncryptor - Encryption Application

# Default virtual environment directory
VENV_DIR := .venv

# Python version to install via pyenv
PYTHON_VERSION := 3.13.4

# Use pyenv's shim if available, otherwise fall back to system python
PY := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Project directories
SRC_DIR := src
MAIN_SCRIPT := $(SRC_DIR)/user_interface.py

.PHONY: help
help:
	@echo "TinyEncryptor - Makefile Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  brew       - Install Homebrew prerequisites (pyenv)"
	@echo "  pyenv      - Install Python $(PYTHON_VERSION) via pyenv"
	@echo "  venv       - Create virtual env with Python $(PYTHON_VERSION)"
	@echo "  install    - Install dependencies from requirements.txt"
	@echo "  sync       - Sync dependencies using uv (faster alternative)"
	@echo "  upgrade    - Upgrade all deps to latest within constraints"
	@echo ""
	@echo "Application Commands:"
	@echo "  run        - Run the application UI (user_interface.py)"
	@echo "  main       - Run the main.py module directly"
	@echo ""
	@echo "Build Commands:"
	@echo "  build      - Build executable for current platform"
	@echo "  build-app  - Build macOS .app bundle"
	@echo "  build-onefile - Build single-file executable"
	@echo "  install-pyinstaller - Install PyInstaller for building"
	@echo ""
	@echo "Development Commands:"
	@echo "  format     - Format code with ruff"
	@echo "  lint       - Lint code with ruff"
	@echo "  check      - Run both format and lint checks"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test       - Run tests (if available)"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  freeze     - Regenerate requirements.txt from current venv"
	@echo "  clean      - Remove virtual env and cache files"
	@echo "  clean-keys - Remove generated key files (use with caution!)"
	@echo "  clean-all  - Remove everything (venv, cache, keys, settings)"
	@echo "  clean-build - Remove build artifacts and dist folders"

.PHONY: brew
brew:
	@command -v brew >/dev/null 2>&1 || { echo "Homebrew not found. Install from https://brew.sh"; exit 1; }
	brew update
	brew install pyenv ||  true
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
		echo "Dependencies installed successfully."; \
	else \
		echo "requirements.txt not found. Run 'make freeze' after installing packages."; \
	fi

.PHONY: sync
sync:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync
	@echo "Dependencies synced with uv."

.PHONY: upgrade
upgrade: venv
	@if [ -f requirements.txt ]; then \
		$(PIP) install --upgrade -r requirements.txt; \
		echo "Dependencies upgraded successfully."; \
	else \
		echo "requirements.txt not found. Run 'make install' first."; \
	fi

.PHONY: freeze
freeze: venv
	$(PIP) freeze > requirements.txt
	@echo "requirements.txt updated from current environment."

.PHONY: run
run:
	@echo "Starting TinyEncryptor UI..."
	@command -v uv >/dev/null 2>&1 && uv run $(MAIN_SCRIPT) || $(PY) $(MAIN_SCRIPT)

.PHONY: main
main:
	@echo "Running main.py module..."
	@command -v uv >/dev/null 2>&1 && uv run $(SRC_DIR)/main.py || $(PY) $(SRC_DIR)/main.py

.PHONY: format
format: venv
	@command -v ruff >/dev/null 2>&1 || $(PIP) install ruff
	@echo "Formatting code with ruff..."
	ruff format $(SRC_DIR)
	@echo "Code formatted successfully."

.PHONY: lint
lint: venv
	@command -v ruff >/dev/null 2>&1 || $(PIP) install ruff
	@echo "Linting code with ruff..."
	ruff check $(SRC_DIR)

.PHONY: check
check: format lint
	@echo "Code check completed."

.PHONY: test
test: venv
	@if [ -d tests ]; then \
		$(PY) -m pytest tests/ -v; \
	else \
		echo "No tests directory found."; \
	fi

.PHONY: install-pyinstaller
install-pyinstaller: venv
	@echo "Installing PyInstaller..."
	$(PIP) install pyinstaller
	@echo "PyInstaller installed successfully."

.PHONY: build
build: install-pyinstaller
	@echo "Building TinyEncryptor executable..."
	$(PY) -m PyInstaller --name="TinyEncryptor" \
		--windowed \
		--onedir \
		--icon="" \
		--add-data="$(SRC_DIR):src" \
		--hidden-import="PIL._tkinter_finder" \
		$(MAIN_SCRIPT)
	@echo "Build complete! Executable in dist/TinyEncryptor/"

.PHONY: build-app
build-app: install-pyinstaller
	@echo "Building TinyEncryptor.app for macOS..."
	$(PY) -m PyInstaller --name="TinyEncryptor" \
		--windowed \
		--onedir \
		--osx-bundle-identifier="com.tinyencryptor.app" \
		--add-data="$(SRC_DIR):src" \
		--hidden-import="PIL._tkinter_finder" \
		$(MAIN_SCRIPT)
	@echo "Build complete! Application at dist/TinyEncryptor.app"

.PHONY: build-onefile
build-onefile: install-pyinstaller
	@echo "Building single-file TinyEncryptor executable..."
	$(PY) -m PyInstaller --name="TinyEncryptor" \
		--windowed \
		--onefile \
		--add-data="$(SRC_DIR):src" \
		--hidden-import="PIL._tkinter_finder" \
		$(MAIN_SCRIPT)
	@echo "Build complete! Single file at dist/TinyEncryptor"

.PHONY: clean-build
clean-build:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.spec
	@echo "Build artifacts removed."

.PHONY: clean
clean:
	@echo "Cleaning up virtual environment and cache files..."
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup completed."

.PHONY: clean-keys
clean-keys:
	@echo "⚠️  WARNING: This will delete all generated key files!"
	@echo "Files to be deleted:"
	@find $(SRC_DIR) -name "*_key.pem" -o -name "*key*.txt" -o -name "*encrypted*.txt" 2>/dev/null || true
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	@find $(SRC_DIR) -name "*_key.pem" -delete 2>/dev/null || true
	@find $(SRC_DIR) -name "*key*.txt" -delete 2>/dev/null || true
	@find $(SRC_DIR) -name "*encrypted*.txt" -delete 2>/dev/null || true
	@echo "Key files removed."

.PHONY: clean-all
clean-all: clean
	@echo "⚠️  WARNING: This will delete everything including keys and settings!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	rm -f $(SRC_DIR)/settings.json
	rm -f $(SRC_DIR)/*.pem
	rm -f $(SRC_DIR)/*key*.txt
	rm -f $(SRC_DIR)/*encrypted*.txt
	rm -f $(SRC_DIR)/encrypted_data.json
	@echo "All project files cleaned."
