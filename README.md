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
deviceIdentification/
├── code/
│  ├── PeriodProcess/                     # Preprocesses idle-time traffic
│  ├── preProcess/
│  ├── SignatureGeneration/
│  ├── testProcessCode/
├── code/
├── code/
├── README.md                          # This file
├── LICENSE                            # The project's license
└── .gitignore                         # Specifies files/folders to ignore in version control


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
