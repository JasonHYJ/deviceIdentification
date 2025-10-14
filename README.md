# Device Identification via Adaptive Periodic Traffic Fingerprints

This repository contains the artifact for our ACSAC 2025 paper:  
**"A Period-Adaptive Traffic Fingerprint-Based Method for Smart Home Device Identification"**  

The method segments IoT device traffic according to the periodicity of communication sessions, extracts key packet fingerprints, and applies a hierarchical matching mechanism to identify device types. It is designed to enable **real-time smart home device monitoring** and achieves **98.82% accuracy** on public datasets.

---

## 📂 Repository Structure

```plaintext
.
├── artifact/                # Main artifact contents
│  ├── PeriodProcess/        # Scripts for periodic session detection
│  ├── preProcess/           # Feature extraction and clustering
│  ├── SignatureGeneration/  # Fingerprint construction using headers & LSH
│  ├── signatureMatching/    # Signature library merging and matching (demo version)
│  ├── testProcessCode/      # Auxiliary evaluation scripts (e.g., confusion matrix)
│  ├── data/
│  │  ├── samples/           # Small sample PCAPs for demo
│  │  ├── cached/            # Optional cached outputs to skip long steps
│  │  └── README.md
│  ├── outputs/              # Output directories (empty by default, filled after run)
│  ├── configs/              # Default parameters (params.yaml)
│  ├── run_demo.sh           # One-click demo script
│  └── README.md             # Description of artifact/ subdir
├── claims/                  # Reproducibility claims (≥1 required)
│  └── claim1/
│     ├── claim.txt
│     ├── run.sh
│     └── expected/
├── infrastructure/          # Supported public infra information
│  └── README.md
├── install.sh               # One-click installation
├── requirements.txt         # Python dependencies
├── README.txt               # Top-level ACSAC artifact instructions
├── README.md                # (this file) GitHub project overview
├── license.txt              # License (Apache 2.0)
└── use.txt                  # Intended use and limitations
├── LICENSE                            # The project's license
└── .gitignore                         # Specifies files/folders to ignore in version control
```
---

## Environment Setup

This artifact runs on **Linux (Ubuntu 20.04/22.04)** or **Google Colab** with **Python 3.8+**.

To install dependencies:

```
cd deviceIdentification
chmod +x install.sh
./install.sh
```

- Dependencies include:
  - numpy
  - pandas
  - scikit-learn
  - matplotlib
  - tqdm
  - scapy
  - pyshark
  - scipy
  - seaborn
  - openpyxl


Note: Executable Permissions
----------------------
Some scripts require execution permission before running. If you encounter
"Permission denied" when executing a script, please grant permission using:

    cd deviceIdentification
    chmod +x install.sh
    chmod +x artifact/run_demo.sh
    chmod +x claims/claim1/run.sh

## Running the Demo:

Run the full pipeline on the provided sample PCAP:

```
chmod +x artifact/run_demo.sh
./artifact/run_demo.sh
```

The pipeline will:

1. Segment traffic into sessions (PeriodProcess)
2. Extract features and cluster packets (preProcess)
3. Generate device fingerprints (SignatureGeneration)
4. Merge signatures into a library (signatureMatching)

Outputs are written to `artifact/outputs/`.
 If cached results exist in `artifact/data/cached/`, they will be reused to shorten runtime.

## Reproducing Claims

Reproducibility claims are located in the `claims/` directory.

For example, to reproduce **Claim 1** (accuracy ≥ 0.97 on demo data):

```
chmod +x claims/claim1/run.sh
./claims/claim1/run.sh
```

Expected validation files are under `claims/claim1/expected/`.

## Dataset and Results:

### Dataset:

​	The public dataset used in the experiments is available under the conditions specified by the source.

​	Mon(IoT)r dataset: https://moniotrlab.khoury.northeastern.edu/publications/imc19/.

​	UNSW 2016 dataset: https://iotanalytics.unsw.edu.au/iottraces.html.

​	CIC IoT dataset 2022 dataset: https://www.unb.ca/cic/datasets/iotdataset-2022.html.

​	yourthings dataset: https://yourthings.info/.

​	Self-collected datasets can be obtained by contacting us.

 For the demo, only small anonymized PCAP snippets are included under `artifact/data/samples/`.

## License and Usage

This project is released under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.

No sensitive information is included in the provided datasets.  See [use.txt](use.txt) for limitations.

The code in this repository is intended for academic research purposes. The datasets used in the experiments are publicly available and can be accessed as described above.

## Summary of Executable Scripts

| Script                 | Purpose                               |
| ---------------------- | ------------------------------------- |
| `install.sh`           | Installs dependencies                 |
| `artifact/run_demo.sh` | Runs the entire demo pipeline         |
| `claims/claim1/run.sh` | Validates the main experimental claim |


