#!/usr/bin/env bash
set -euo pipefail

# Create a virtual environment (optional, but recommended)
# python3 -m venv venv
# source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "[OK] Environment setup complete."
