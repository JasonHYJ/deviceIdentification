# deviceIdentification
Smart home device identification using adaptive periodic traffic fingerprints for real-time device monitoring.
## Overview
This artifact provides the source code for our paper on smart home device identification using adaptive periodic traffic fingerprints. The method segments traffic based on the periodicity of IoT device communication sessions, extracts key packet features, and uses a two-stage hierarchical matching mechanism for device type identification. This approach achieves high accuracy (98.82%) and can identify devices even with incomplete traffic data.

This repository includes the code, a subset of public datasets, and the result visualizations corresponding to the experiments presented in the paper.

---

## Project Structure

The repository is organized into the following folders:

### 1. `artifact/` (Code)
This folder contains the source code implementing the key steps of the identification pipeline:
.
├─ README.txt # Top-level overview and execution guide (required)
├─ install.sh # One-click installation script (recommended)
├─ requirements.txt # Dependency list (recommended)
├─ license.txt # License name and URL (corresponding to the LICENSE file in the repository)
├─ use.txt # Intended use and limitations (research purposes, no sensitive data, etc.)
├─ artifact/ # Main code folder (equivalent to the original code/ folder)
│ ├─ PeriodProcess/ # Scripts for preprocessing idle traffic and session segmentation
│ ├─ preProcess/ # Feature extraction and clustering for identifying key packets
│ ├─ SignatureGeneration/ # Generates device fingerprints based on header features and payload LSH
│ ├─ SignatureMatching/ # Matching test samples to the stored device fingerprints
│ ├─ testProcessCode/ # Auxiliary scripts for evaluation, such as confusion matrix generation
│ └─ data/ # Subset of datasets and instructions for obtaining the full datasets
│ ├─ samples/ # Optional: minimal subset for offline testing
│ └─ README.md # Dataset explanation and download instructions
├─ scripts/ # Scripts to run different stages of the pipeline
│ ├─ run_all.sh # Sequentially calls all stages (as per numbering in original scripts)
│ ├─ run_preprocess.sh # Calls preprocessing scripts
│ ├─ run_fingerprint.sh # Calls fingerprint generation scripts
│ └─ run_match.sh # Calls the matching script
├─ claims/ # Folder for reproducibility claims and validation (optional)
│ └─ claim1/ # Example claim folder (e.g., accuracy claim)
│ ├─ claim.txt # Brief description of the claim
│ ├─ run.sh # Script to reproduce the claim result
│ └─ expected/ # Expected output or validation information (e.g., accuracy threshold)
└─ infrastructure/ # Folder for infrastructure setup or platform instructions
└─ README.md # Instructions for running the code on public platforms (e.g., Google Colab)

---

## Environment Setup

This project requires Python 3.8 and runs on Linux-based systems. The following dependencies are needed to run the code:

### Dependencies:
- Python 3.8
- numpy
- scipy
- scikit-learn
- pandas
- tqdm
- matplotlib
- pcap libraries (e.g., scapy, pyshark)

To install the required dependencies, use the following command:

```bash
pip install -r requirements.txt
