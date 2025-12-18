#!/usr/bin/env bash
set -euo pipefail

# Create virtualenv if it doesn't exist
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

source .venv/bin/activate

# Install dependencies (helpful message on network/proxy failure)
if ! pip install -r backend/requirements.txt; then
  echo "Dependency installation failed. If you are behind a proxy or offline, configure pip networking (e.g., --proxy) or preinstall wheels before running tests." >&2
  exit 1
fi

python -m pytest backend/tests
