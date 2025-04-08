#!/usr/bin/env bash

set -euo pipefail

VERSION="${1}"
RELEASE="${2}"

# Pulls the existing changelog already in the spec file. This is generated
# by Tito.
CHANGELOG="$(./scripts/spec-changelog.py)"

export VERSION
export RELEASE
export CHANGELOG

gomplate -f ./crystalfontz.spec.tmpl -o crystalfontz.spec
