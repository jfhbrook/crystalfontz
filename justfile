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

# Run crystalfontz client cli
client *argv:
  uv run -- python -m crystalfontz {{ argv }}

# Run crystalfontz.dbus.service cli
service *argv:
  uv run -- python -m crystalfontz.dbus.service --user {{ argv }}

# Run crystalfontz.dbus.client cli
dbus-client *argv:
  uv run -- python -m crystalfontz.dbus.client --user {{ argv }}


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

# Install systemd service files and dbus config for development purposes
install-service:
  sudo install -p -D -m 0644 systemd/crystalfontz.service /usr/lib/systemd/system/crystalfontz.service
  sudo install -p -D -m 0644 dbus/org.jfhbrook.crystalfontz.conf /usr/share/dbus-1/system.d/org.jfhbrook.crystalfontz.conf

# Pull the crystalfontz service's logs with journalctl
service-logs:
  journalctl -xeu crystalfontz.service

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

clean-build:
  rm -rf dist

# Generate crystalfontz.spec
generate-spec:
  ./scripts/generate-spec.sh "$(./scripts/version.py)" "$(./scripts/release-version.py)"

# Update the package version in ./copr/python-crystalfontz.yml
copr-update-version:
  VERSION="$(./scripts/version.py)" yq -i '.spec.packageversion = strenv(VERSION)' ./copr/python-crystalfontz.yml

# Commit generated files
commit-generated-files:
  git add requirements.txt
  git add requirements_dev.txt
  git add crystalfontz.spec
  git add ./copr
  git commit -m 'Update generated files' || echo 'No changes to files'

# Fail if there are uncommitted files
check-dirty:
  ./scripts/is-dirty.sh

# Fail if not on the main branch
check-main-branch:
  ./scripts/is-main-branch.sh

# Tag the release with tito
tag:
  ./scripts/tag.sh

# Push main and tags
push:
  git push origin main --follow-tags

# Publish package to PyPI
publish-pypi: build
  uv publish -t "$(op item get 'PyPI' --fields 'API Token' --reveal)"

# Create a GitHub release
gh-release:
  bash ./scripts/gh-release.sh "$(./scripts/version.py)-$(./scripts/release-version.py)"

# Apply a COPR package configuration
apply-copr package:
  coprctl apply -f ./copr/{{ package }}.yml

# Build a COPR package
build-copr package:
  copr build-package jfhbrook/joshiverse --name '{{ package }}'

# Publish the release on PyPI, GitHub and Copr
publish:
  # Generate files and commit
  @just compile
  @just generate-spec
  @just copr-update-version
  @just commit-generated-files
  # Ensure git is in a good state
  @just check-main-branch
  @just check-dirty
  # Tag and push
  @just tag
  @just push
  # Build package and bundle release
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just clean-build; fi
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just build; fi
  # Publish package and release
  @just gh-release
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just publish-pypi; fi
  # Update packages on COPR
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just apply-copr python-crystalfontz; fi
  @just apply-copr crystalfontz
  if [[ "$(./scripts/release-version.py)" == '1' ]]; then just build-copr python-crystalfontz; fi
  @just build-copr crystalfontz

# Clean up loose files
clean: _clean-venv _clean-compile _clean-test
  rm -rf crystalfontz.egg-info
  rm -f crystalfontz/*.pyc
  rm -rf crystalfontz/__pycache__
