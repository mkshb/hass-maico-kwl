#!/usr/bin/env bash
# Which checks a change needs, as name=true|false lines for $GITHUB_OUTPUT.
#
# Usage: changes.sh [BASE]
# Compares BASE with HEAD. Without BASE (a scheduled or manual run) every
# check runs.
set -euo pipefail

base="${1:-}"
files=""
if [ -n "$base" ]; then
  files=$(git diff --name-only "$base" HEAD)
  printf 'Changed files:\n%s\n' "$files" >&2
fi

# check NAME PATTERN: true if a changed file matches the extended regex.
check() {
  if [ -z "$base" ] || grep -q -E "$2" <<< "$files"; then
    echo "$1=true"
  else
    echo "$1=false"
  fi
}

# A change to the workflows or to this script runs everything.
ci='^\.github/(workflows|scripts)/'

# tests/test_manifest.py reads CHANGELOG.md and hacs.json,
# tests/test_frontend.py the entity keys of the card.
check python "$ci|^custom_components/|^tests/|^blueprints/|^requirements_test\.txt$|^pyproject\.toml$|^CHANGELOG\.md$|^hacs\.json$|^frontend-src/src/keys\.ts$"
# The CI compares the committed build with the sources.
check card "$ci|^frontend-src/|^custom_components/maico_kwl/frontend/"
check hassfest "$ci|^custom_components/"
check hacs "$ci|^custom_components/|^hacs\.json$|^README\.md$"
