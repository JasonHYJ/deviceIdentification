# deviceIdentification
Smart home device identification using adaptive periodic traffic fingerprints for real-time device monitoring.
## Overview
This artifact provides the source code for our paper on smart home device identification using adaptive periodic traffic fingerprints. The method segments traffic based on the periodicity of IoT device communication sessions, extracts key packet features, and uses a two-stage hierarchical matching mechanism for device type identification. This approach achieves high accuracy (98.82%) and can identify devices even with incomplete traffic data.

This repository includes the code, a subset of public datasets, and the result visualizations corresponding to the experiments presented in the paper.

---

## Project Structure

### 1. `artifact/` (Code)
This folder contains the source code implementing the key steps of the identification pipeline:
- **PeriodProcess/**: Scripts for preprocessing idle traffic and segmenting sessions based on periodicity.
- **preProcess/**: Feature extraction and clustering to identify key packets.
- **SignatureGeneration/**: Generates device fingerprints based on header features and payload LSH.
- **SignatureMatching/**: Matching test samples to the stored device fingerprints.
- **testProcessCode/**: Auxiliary scripts for evaluation, including generating confusion matrices and splitting pcap files by MAC address.

### 2. `data/` (Datasets)
This folder contains:
- A small subset of public datasets used for testing.
- Some private pcap samples used for training (without any sensitive data).
- A `README.md` file that explains how to obtain the full dataset or generate new ones.

### 3. `results/` (Results)
This folder includes:
- **figures/**: Generated visualizations such as confusion matrices, ROC curves, and feature importance plots.
- **csv/**: Output files such as extracted features and fingerprints.
- **logs/**: Log files for the execution of the scripts, which capture details of the runtime.

---
