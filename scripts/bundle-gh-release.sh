#!/usr/bin/env bash

set -euo pipefail

FULL_VERSION="${1}"

tar -czf "crystalfontz-${FULL_VERSION}.tar.gz" \
  CHANGELOG.md \
  LICENSE \
  README.md \
  docs \
  crystalfontz \
  crystalfontz.spec \
  pyproject.toml \
  pytest.ini \
  requirements.txt \
  requirements_dev.txt \
  setup.cfg \
  systemd \
  tests \
  typings \
  uv.lock
