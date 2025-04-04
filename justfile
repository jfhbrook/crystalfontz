set dotenv-load := true

# By default, run checks and tests, then format and lint
default:
  if [ ! -d venv ]; then just install; fi
  @just format
  @just check
  @just test
  @just lint

#
# Installing, updating and upgrading dependencies
#

_venv:
  if [ ! -d .venv ]; then uv venv; fi

_clean-venv:
  rm -rf .venv

# Install all dependencies
install:
  @just _venv
  if [[ "$(uname -s)" == Linux ]]; then uv sync --dev --extra dbus; else uv sync --dev; fi
  uv pip install -e .

# Update all dependencies
update:
  @just install

# Update all dependencies and rebuild the environment
upgrade:
  if [ -d venv ]; then just update && just check && just _upgrade; else just update; fi

_upgrade:
  @just _clean-venv
  @just _venv
  @just install

# Generate locked requirements files based on dependencies in pyproject.toml
compile:
  uv pip compile -o requirements.txt pyproject.toml
  cp requirements.txt requirements_dev.txt
  python3 -c 'import tomllib; print("\n".join(tomllib.load(open("pyproject.toml", "rb"))["dependency-groups"]["dev"]))' >> requirements_dev.txt

_clean-compile:
  rm -f requirements.txt
  rm -f requirements_dev.txt

#
# Development tooling - linting, formatting, etc
#

# Run a command or script
run *argv:
  uv run {{ argv }}

# Run crystalfontz cli
start *argv:
  uv run -- python -m crystalfontz {{ argv }}

# Format with black and isort
format:
  uv run  black './crystalfontz' ./tests
  uv run  isort --settings-file . './crystalfontz' ./tests

# Lint with flake8
lint:
  uv run flake8 './crystalfontz' ./tests
  shellcheck ./scripts/*.sh ./bin/*
  uv run validate-pyproject ./pyproject.toml

# Check type annotations with pyright
check:
  uv run npx pyright@latest

# Run tests with pytest
test *argv:
  uv run pytest {{ argv }} ./tests --ignore-glob='./tests/integration/**'
  @just _clean-test

# Update snapshots
snap:
  uv run pytest --snapshot-update ./tests --ignore-glob='./tests/integration/**'
  @just _clean-test

# Run integration tests
integration *argv:
  ./scripts/integration.sh {{ argv }}

_clean-test:
  rm -f pytest_runner-*.egg
  rm -rf tests/__pycache__

# Display the raw XML introspection of the live dbus service
print-iface:
  dbus-send --system --dest=org.jfhbrook.crystalfontz "/" --print-reply org.freedesktop.DBus.Introspectable.Introspect

#
# Shell and console
#

shell:
  uv run bash

console:
  uv run jupyter console


#
# Documentation
#

# Live generate docs and host on a development webserver
docs:
  uv run mkdocs serve

# Build the documentation
build-docs:
  uv run mkdocs build

# Render markdown documentation based on the live service from dbus
generate-dbus-iface-docs *ARGV:
  @bash ./scripts/generate-dbus-iface-docs.sh {{ ARGV }}

#
# Package publishing
#

# Build the package
build:
  uv build

_clean-build:
  rm -rf dist

# Tag the release in git
tag:
  uv run git tag -a "$(python3 -c 'import toml; print(toml.load(open("pyproject.toml", "r"))["project"]["version"])')" -m "Release $(python3 -c 'import toml; print(toml.load(open("pyproject.toml", "r"))["project"]["version"])')"

# Build the package and publish it to PyPI
publish: build
  uv publish

# Clean up loose files
clean: _clean-venv _clean-compile _clean-test
  rm -rf crystalfontz.egg-info
  rm -f crystalfontz/*.pyc
  rm -rf crystalfontz/__pycache__
