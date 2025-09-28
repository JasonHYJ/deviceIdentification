# Artifact Directory

This directory contains the core implementation, data samples, and execution scripts for artifact evaluation.

## Contents

- **PeriodProcess/**: Scripts for preprocessing raw PCAPs and detecting periodic sessions.
- **preProcess/**: Scripts for feature extraction, clustering, and session filtering.
- **SignatureGeneration/**: Scripts for generating device fingerprints using header features and LSH.
- **signatureMatching/**: Scripts for merging device signatures and performing basic matching (optional).
- **testProcessCode/**: Auxiliary scripts such as MAC-based PCAP splitting and confusion matrix evaluation.
- **data/**:
  - `samples/`: small sample PCAPs to run the demo, and csv file for test.
  - `cached/`: optional cached intermediate results to skip earlier stages.
- **outputs/**: target directory for all pipeline outputs (with `.gitkeep` placeholders).
- **configs/**: default parameter settings (`params.yaml`) and documentation.
- **run_demo.sh**: entry script to run the full pipeline with optional cache skipping.

## Usage

To run the demo pipeline:

```bash
bash run_demo.sh
```