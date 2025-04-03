#!/usr/bin/env bash

set -euo pipefail

COMPONENTS=()
ARGV=()

while [[ $# -gt 0 ]]; do
  case "${1}" in
    --system)
      ARGV+=(--system)
      shift
      ;;
    *)
      COMPONENTS+=("${1}")
      shift
      ;;
  esac
done

if [ ${#COMPONENTS[@]} -eq 0 ]; then
  COMPONENTS=("crystalfontz")
fi

for component in "${COMPONENTS[@]}"; do
  ARGV+=("./tests/integration/test_${component}.py")
done

set -x

exec uv run gaktest "${ARGV[@]}"
