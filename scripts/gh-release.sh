#!/usr/bin/env bash

set -euo pipefail

FULL_VERSION="${1}"

NOTES="$(./scripts/changelog-entry.py "${FULL_VERSION}")"

gh release create "crystalfontz-${FULL_VERSION}" \
  -t "crystalfontz v${FULL_VERSION}" \
  -n "${NOTES}"
