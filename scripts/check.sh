#!/usr/bin/env bash
# Run the same checks as CI, in order. Usage: scripts/check.sh
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q
