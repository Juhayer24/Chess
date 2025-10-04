#!/usr/bin/env bash
# Simple helper to create a venv, install requirements and run the game on macOS/Unix shells (zsh/bash)
set -euo pipefail

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Activate venv
# shellcheck source=/dev/null
source .venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run the game
python3 main.py
