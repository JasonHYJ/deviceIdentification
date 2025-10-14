Artifact for ACSAC 2025
=======================

Title: A Period-Adaptive Traffic Fingerprint-Based Method for Smart Home Device Identification
Authors: Yingjie Hu

Overview
--------
This artifact contains the source code, sample datasets, and evaluation scripts
for reproducing the main results of our ACSAC 2025 paper. The method segments IoT
traffic based on communication periodicity, extracts key packet fingerprints, and
performs hierarchical matching to identify device types.

Directory Layout
----------------
- artifact/        Main source code, sample data, configs, outputs, run script
- claims/          Paper claims and reproduction scripts
- infrastructure/  Information on supported public infrastructure
- install.sh       One-click environment setup script
- requirements.txt Python dependencies
- license.txt      License information
- use.txt          Intended use and limitations

Installation
------------
To set up the environment, run:

    ./install.sh

This will install all required dependencies listed in `requirements.txt`.

Executable Permissions
----------------------
Some scripts require execution permission before running. If you encounter
"Permission denied" when executing a script, please grant permission using:
    
    cd deviceIdentification
    chmod +x install.sh
    chmod +x artifact/run_demo.sh
    chmod +x claims/claim1/run.sh

After this step, you can run the scripts directly with:

    ./install.sh
    ./artifact/run_demo.sh
    ./claims/claim1/run.sh


The pipeline will:
1. Process a sample PCAP trace
2. Detect periodic sessions
3. Extract features and cluster packets
4. Generate device fingerprints
5. Optionally merge signatures into a library

If cached intermediate results exist under `artifact/data/cached/`, the pipeline
will reuse them to reduce runtime.

Reproducing Claims
------------------
Each claim can be validated from the `claims/` directory.

Example (Claim 1: 98.82% accuracy on Mon(IoT)r dataset):

    ./claims/claim1/run.sh

Expected results and validation criteria are in:

    claims/claim1/expected/check.json

Infrastructure
--------------
The artifact runs on standard Linux environments. Tested on:

- Google Colab (Ubuntu 22.04, Python 3.8)
- CloudLab (Ubuntu 20.04, Python 3.8)

No GPU is required.

Contact
-------
If you encounter issues during evaluation, please contact the authors.

