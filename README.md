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
│  ├── PeriodProcess/                     # Scripts for preprocessing idle traffic, segmenting the sessions based on their periodicity.
│  ├── preProcess/                        # Feature extraction and clustering for identifying key packets in each session.
│  ├── SignatureGeneration/               # Generates device fingerprints based on packet headers and payloads using Local Sensitive Hashing (LSH).
│  ├── testProcessCode/                   # Auxiliary scripts for evaluation, including generating confusion matrices and splitting pcap files by MAC address.
├── datasets and result/               # This folder contains links to public datasets, portions of our proprietary datasets, and some experimental results.
├── README.md                          # This file is project description.
├── LICENSE                            # The project's license
└── .gitignore                         # Specifies files/folders to ignore in version control
```
---

## Environment Setup

This project requires Python 3.8 and runs on Linux-based systems. The following dependencies are needed to run the code:

### Dependencies:
- Python 3.8
- numpy
- scikit-learn
- pandas
- tqdm
- matplotlib
- pcap libraries (e.g., scapy, pyshark)

To install the required dependencies, use the following command:

```bash
pip install -r requirements.txt

### How to Run the Code:

The pipeline is divided into several stages. Follow the steps below to run the code:

1. Period Process: Run the scripts to process the idle traffic and segment the sessions based on their periodicity.

2. Pre-processing: Extract features and perform clustering to identify key packets.

3. Signature Generation: Generate device fingerprints based on header features and payload LSH.

Each folder contains scripts that should be run sequentially. The results of each stage are saved in separate output directories.

### Dataset and Results:

Dataset:

  The public dataset used in the experiments is the [XYZ dataset](link to dataset), available under the conditions specified by the source.
  
  A small subset of the dataset is included in the data/ folder for testing purposes.
  
  The full dataset can be obtained by following the instructions in data/README.md.

