#!/usr/bin/env bash
set -euo pipefail

# Run the demo pipeline
bash artifact/run_demo.sh

# After pipeline finishes, evaluate the output
python3 artifact/testProcessCode/evaluate_confusion_matrix.py \
    --input artifact/data/samples/testCsv/uk_confusion_matrix.csv \
    --output artifact/outputs/eval/confusion_matrix.pdf

echo "[OK] Claim 1 reproduction complete. See artifact/outputs/eval/ for results."
