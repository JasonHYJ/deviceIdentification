# -- coding: utf-8 --

"""
并行版：从 suitableDir 下批量对 .pcap 提取 CSV 特征，追加 direction/time_interval 两列。
改进点：
1) 多进程按“文件粒度”并行（--workers），默认=CPU核心数；
2) 智能降级 tshark 字段（遇到 “Some fields aren't valid” 自动移除问题字段并重试）；
3) 方向判定仅用该设备目录推断到的 MAC（更快）；
4) 已有且含 direction 列的 CSV 可跳过（--skip-existing）。

用法：
python 2_featureExtraction.py \
  --source /home/hyj/deviceIdentification/dataset/yorthings/4_suitableDir \
  --dest   /home/hyj/deviceIdentification/dataset/yorthings/featureCsv \
  --workers 16 --no-skip-existing
"""

import os
import csv
import subprocess
import argparse
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

# ======= 你的设备 MAC 映射，保持原样粘贴完整 =======
device_mac_mapping = {
    # ...... 请粘贴你给的完整映射表 ......
    "NetgearArloCamera": "b0:7f:b9:a6:47:4d",
}

# 期望抽取的字段（会自动降级剔除不被支持的字段）
PREFERRED_FIELDS = [
    "frame.time_epoch",
    "frame.protocols",
    "frame.len",
    "eth.src",
    "eth.dst",
    "ip.src",
    "ip.dst",
    "ip.len",
    "tcp.len",
    "udp.length",
    "ip.ttl",
    "tcp.srcport",
    "tcp.dstport",
    "udp.srcport",
    "udp.dstport",
    "tcp.flags",
    "tls.record.content_type",
    "tcp.window_size",
    "_ws.expert.message",
    "tcp.payload",
    "udp.payload",  # 有些版本不支持；脚本会自动剔除
]

# ---------------- 工具函数 ----------------

def run_tshark_fields(pcap_path: str, fields: list, out_csv_path: str) -> subprocess.CompletedProcess:
    args = ["tshark", "-r", pcap_path, "-T", "fields"]
    for f in fields:
        args += ["-e", f]
    args += ["-E", "header=y", "-E", "separator=,", "-E", "quote=d", "-E", "occurrence=f"]
    with open(out_csv_path, "w", newline="") as fh_out:
        proc = subprocess.run(args, stdout=fh_out, stderr=subprocess.PIPE, text=True)
    return proc

def parse_invalid_fields(stderr_text: str) -> list:
    invalid = []
    if not stderr_text:
        return invalid
    lines = stderr_text.splitlines()
    flag = False
    for line in lines:
        if "Some fields aren't valid" in line:
            flag = True
            continue
        if flag:
            name = line.strip()
            if name:
                invalid.append(name)
    return invalid

def infer_device_name_from_path(source_root: str, pcap_path: str) -> str:
    rel = os.path.relpath(os.path.dirname(pcap_path), start=source_root)
    parts = rel.split(os.sep)
    return parts[0] if parts else ""

def normalize_mac(mac: str) -> str:
    return mac.strip().lower() if mac else ""

def csv_has_direction(dest_csv: str) -> bool:
    if not os.path.exists(dest_csv):
        return False
    try:
        with open(dest_csv, "r", newline="") as f:
            r = csv.reader(f)
            header = next(r, None)
            return (header is not None) and ("direction" in header)
    except Exception:
        return False

# ---------------- 单文件处理（子进程执行） ----------------

def process_one_file(pcap_file: str, source_root: str, dest_root: str, skip_existing: bool = True) -> tuple:
    """
    返回 (pcap_file, ok:bool, msg:str)
    """
    try:
        # 目标 CSV 路径
        rel_dir = os.path.relpath(os.path.dirname(pcap_file), source_root)
        dest_dir = os.path.join(dest_root, rel_dir)
        os.makedirs(dest_dir, exist_ok=True)
        dest_csv = os.path.join(dest_dir, os.path.basename(pcap_file)[:-5] + ".csv")

        if skip_existing and csv_has_direction(dest_csv):
            return (pcap_file, True, "skip-existing")

        # 设备 MAC
        dev_name = infer_device_name_from_path(source_root, pcap_file)
        dev_mac = normalize_mac(device_mac_mapping.get(dev_name))

        # 逐步降级字段跑 tshark
        fields = list(PREFERRED_FIELDS)
        tried = set()
        for _ in range(4):
            proc = run_tshark_fields(pcap_file, fields, dest_csv)
            if proc.returncode == 0:
                break
            invalid = parse_invalid_fields(proc.stderr)
            if not invalid:
                # 经验性剔除（常见不兼容）
                fallbacks = [f for f in ["udp.payload", "_ws.expert.message", "tcp.payload"] if f in fields]
                if fallbacks:
                    for f in fallbacks:
                        fields.remove(f)
                    continue
                return (pcap_file, False, f"tshark failed: {proc.stderr.strip()[:200]}")
            changed = False
            for bad in invalid:
                if bad in fields and bad not in tried:
                    fields.remove(bad); tried.add(bad); changed = True
            if not changed:
                return (pcap_file, False, f"tshark failed: {proc.stderr.strip()[:200]}")

        if proc.returncode != 0:
            return (pcap_file, False, f"tshark failed: {proc.stderr.strip()[:200]}")

        # 追加 direction / time_interval
        tmp_csv = dest_csv + ".tmp"
        with open(dest_csv, "r", newline="") as infile, open(tmp_csv, "w", newline="") as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            headers = next(reader, None)
            if headers is None:
                return (pcap_file, False, "empty csv")

            # 列索引
            try:
                col_time = headers.index("frame.time_epoch")
            except ValueError:
                col_time = None
            try:
                col_src = headers.index("eth.src")
                col_dst = headers.index("eth.dst")
            except ValueError:
                col_src = col_dst = None

            # 已有就覆盖写
            if "direction" not in headers:
                headers.append("direction")
            if "time_interval" not in headers:
                headers.append("time_interval")
            writer.writerow(headers)

            prev_time = None
            for row in reader:
                # 时间
                if col_time is not None and col_time < len(row) and row[col_time]:
                    try:
                        curr_time = float(row[col_time])
                    except ValueError:
                        curr_time = None
                else:
                    curr_time = None

                # 方向
                direction = 0
                if dev_mac and col_src is not None and col_dst is not None:
                    src_mac = normalize_mac(row[col_src]) if col_src < len(row) else ""
                    dst_mac = normalize_mac(row[col_dst]) if col_dst < len(row) else ""
                    if src_mac == dev_mac:
                        direction = 1
                    elif dst_mac == dev_mac:
                        direction = -1

                # 间隔
                if prev_time is None or curr_time is None:
                    interval = 0.0
                else:
                    interval = max(0.0, curr_time - prev_time)
                if curr_time is not None:
                    prev_time = curr_time

                # 补列（若原文件没有这两列）
                if "direction" in headers and (len(row) < len(headers)):
                    row += [""] * (len(headers) - len(row))
                # 设置末两列
                if "direction" in headers:
                    row[headers.index("direction")] = str(direction)
                if "time_interval" in headers:
                    row[headers.index("time_interval")] = f"{interval:.6f}"

                writer.writerow(row)

        os.replace(tmp_csv, dest_csv)
        return (pcap_file, True, "ok")
    except Exception as e:
        return (pcap_file, False, repr(e))

# ---------------- 主流程（并行调度） ----------------

def enumerate_pcaps(source_root: str):
    for r, _ds, fs in os.walk(source_root):
        for fn in fs:
            if fn.lower().endswith(".pcap"):
                yield os.path.join(r, fn)

def main():
    parser = argparse.ArgumentParser(description="并行提取 PCAP 特征到 CSV（tshark）")
    parser.add_argument("--source", default="artifact/outputs/preproc/4_suitableDir",
                        help="源 .pcap 根目录")
    parser.add_argument("--dest",   default="artifact/outputs/preproc/5_csv",
                        help="输出 .csv 根目录")
    cpu_cnt = multiprocessing.cpu_count()
    parser.add_argument("--workers", type=int, default=cpu_cnt,
                        help=f"并行进程数（默认={cpu_cnt}）")
    parser.add_argument("--skip-existing", dest="skip", action="store_true", default=True,
                        help="若目标 CSV 已存在且含 direction 列则跳过（默认开启）")
    parser.add_argument("--no-skip-existing", dest="skip", action="store_false",
                        help="不跳过已存在 CSV，强制重跑")
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    pcaps = list(enumerate_pcaps(args.source))
    if not pcaps:
        print("[INFO] 未发现 .pcap 文件"); return

    print(f"[CONF] files={len(pcaps)} workers={args.workers} skip_existing={args.skip}")
    ok = fail = 0

    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(process_one_file, p, args.source, args.dest, args.skip) for p in pcaps]
        for i, fut in enumerate(as_completed(futs), 1):
            pcap_file, success, msg = fut.result()
            if success:
                ok += 1
            else:
                fail += 1
            if i % 20 == 0 or not success:
                print(f"[{i}/{len(pcaps)}] {('OK','FAIL')[not success]} :: {pcap_file} :: {msg}")

    print(f"[DONE] total={len(pcaps)} ok={ok} fail={fail}")

if __name__ == "__main__":
    main()
