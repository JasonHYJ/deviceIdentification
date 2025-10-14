#!/usr/bin/env bash
set -euo pipefail

# 定位到 install.sh 所在的仓库根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 升级 pip（使用当前 python）
python3 -m pip install --upgrade pip

# 安装依赖（路径现在指向仓库根，不受你从哪里调用影响）
python3 -m pip install -r requirements.txt

echo "[OK] Environment setup complete."
