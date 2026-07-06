#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

find_python() {
  if [ -n "${PYTHON_BIN:-}" ]; then
    printf '%s\n' "$PYTHON_BIN"
    return
  fi

  for candidate in python3.13 python3.12 python3.11; do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return
    fi
  done

  local codex_python="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
  if [ -x "$codex_python" ]; then
    printf '%s\n' "$codex_python"
    return
  fi

  command -v python3
}

PYTHON="$(find_python)"
"$PYTHON" - <<'PY'
import sys

if sys.version_info < (3, 11):
    raise SystemExit(f"Python >= 3.11 is required, got {sys.version.split()[0]}")
PY

if [ -x ".venv/bin/python" ] && ! .venv/bin/python - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
then
  rm -rf .venv
fi

if [ ! -x ".venv/bin/github-high-potential" ]; then
  "$PYTHON" -m venv .venv
  .venv/bin/pip install -e .
fi

HOURS="${GITHUB_HIGH_POTENTIAL_HOURS:-${TECHNEWS_HOURS:-12}}"
LIMIT="${GITHUB_HIGH_POTENTIAL_LIMIT:-${TECHNEWS_LIMIT:-30}}"

.venv/bin/github-high-potential run --hours "$HOURS" --limit "$LIMIT"
