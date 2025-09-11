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
## Project Structure
The project is organized under the `code` directory with the following hierarchy:

```plaintext
code/
├── PeriodProcess/
│   ├── 1_preprocess_traffic.py        # Preprocesses idle-time traffic
│   ├── 2_analyze_periodicity.py       # Analyzes periodicity using Fourier Transform
│   ├── 3_segment_samples.py           # Segments samples based on session periodicity
│   └── ...                            # Other scripts for adaptive sample segmentation
├── preProcess/
│   ├── 1_extract_features.py          # Extracts features from traffic samples
│   ├── 2_cluster_packets.py           # Clusters packets to identify key packets
│   └── ...                            # Other preprocessing scripts
├── SignatureGeneration/
│   ├── 1_generate_header_features.py  # Extracts header features (length, direction, protocol)
│   ├── 2_compute_lsh.py               # Computes LSH for payload
│   ├── 3_build_fingerprints.py        # Builds device fingerprints from key packets
│   └── ...                            # Other fingerprint generation scripts
├── SignatureMatching/
│   ├── 1_match_packets.py             # Performs packet-level hierarchical matching
├── testProcessCode/
│   ├── 1_split_by_mac.py              # Splits pcap files by device MAC address
│   ├── 2_evaluate_confusion_matrix.py # Generates confusion matrix for evaluation
│   └── ...                            # Other auxiliary scripts

```
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
