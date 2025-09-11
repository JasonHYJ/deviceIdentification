# deviceIdentification
Smart home device identification using adaptive periodic traffic fingerprints for real-time device monitoring.
## Overview
This artifact provides the source code for our paper "A Period-Adaptive Traffic Fingerprint-Based Method for Smart Home Device Identification". The method segments traffic based on the periodicity of IoT device communication sessions, extracts key packet features, and uses a two-stage hierarchical matching mechanism for device type identification. 

This repository includes the code, a subset of public datasets, and the result visualizations corresponding to the experiments presented in the paper.

---

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
```

## How to Run the Code:

The pipeline is divided into several stages. Follow the steps below to run the code:

1. Period Process: Run the scripts to process the idle traffic and segment the sessions based on their periodicity.

2. Pre-processing: Extract features and perform clustering to identify key packets.

3. Signature Generation: Generate device fingerprints based on header features and payload LSH.

Each folder contains scripts that should be run sequentially. The results of each stage are saved in separate output directories.

## Dataset and Results:

### Dataset:

​	The public dataset used in the experiments is available under the conditions specified by the source.

​	Mon(IoT)r dataset: https://moniotrlab.khoury.northeastern.edu/publications/imc19/.

​	UNSW 2016 dataset: https://iotanalytics.unsw.edu.au/iottraces.html.

​	CIC IoT dataset 2022 dataset: https://www.unb.ca/cic/datasets/iotdataset-2022.html.

​	yourthings dataset: https://yourthings.info/.

​	Self-collected datasets can be obtained by contacting us.

### Results:

​	The results of the experiments, including confusion matrices, csv files are available in the `Dataset and Results` folder.

## License and Usage

This project is licensed under the Apache License. See the [LICENSE](LICENSE) file for more information.

The code in this repository is intended for academic research purposes. The datasets used in the experiments are publicly available and can be accessed as described above.



