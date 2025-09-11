# deviceIdentification
Smart home device identification using adaptive periodic traffic fingerprints for real-time device monitoring.
## Overview
This artifact provides the source code for our paper on smart home device identification using adaptive periodic traffic fingerprints. The method segments traffic based on the periodicity of IoT device communication sessions, extracts key packet features, and uses a two-stage hierarchical matching mechanism for device type identification. This approach achieves high accuracy (98.82%) and can identify devices even with incomplete traffic data.

This repository includes the code, a subset of public datasets, and the result visualizations corresponding to the experiments presented in the paper.

---

## Project Structure

├─ README.txt # 顶层总览与执行指南（必须） ├─ install.sh # 一键安装（建议保留，很简短） ├─ requirements.txt # 依赖清单（建议） ├─ license.txt # 许可证名称与URL（与仓库 LICENSE 对应） ├─ use.txt # 预期用途与限制（研究用途、无敏感数据等） ├─ artifact/ # 你的主体代码（等同于原 code/） │ ├─ PeriodProcess/ │ ├─ preProcess/ │ ├─ SignatureGeneration/ │ ├─ SignatureMatching/ │ ├─ testProcessCode/ │ └─ data/ │ ├─ samples/ # 可选：放极小子集，保证离线可跑 │ └─ README.md # 数据说明/下载方式（如需） ├─ scripts/ │ ├─ run_all.sh # 依序调用四阶段脚本（照你编号调用） │ ├─ run_preprocess.sh │ ├─ run_fingerprint.sh │ └─ run_match.sh ├─ claims/ │ └─ claim1/ │ ├─ claim.txt # 例如“在公开数据集达到≈98.82%” │ ├─ run.sh # 跑一个“缩小版”流程（快） │ └─ expected/ │ └─ check.json # 期望指标或阈值（例如 acc ≥ 0.97） └─ infrastructure/ └─ README.md

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
