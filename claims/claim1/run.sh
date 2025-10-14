#!/usr/bin/env bash
set -euo pipefail

# Resolve repo root from this script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 1) Run demo
bash "$REPO_ROOT/artifact/run_demo.sh"

# 2) Evaluate (adjust args if your script differs)
python3 "$REPO_ROOT/artifact/testProcessCode/evaluate_confusion_matrix.py" \
  --input "$REPO_ROOT/artifact/data/samples/testCsv/uk_confusion_matrix.csv" \
  --output "$REPO_ROOT/artifact/outputs/eval/confusion_matrix.pdf"


echo "[OK] Claim 1 reproduction complete. See $REPO_ROOT/artifact/outputs/eval/"
