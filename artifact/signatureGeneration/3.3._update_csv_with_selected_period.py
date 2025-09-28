# -*- coding: utf-8 -*-

"""
该脚本用于更新 CSV 文件中的会话名，添加周期值。周期值从 `source_dir` 中对应设备和会话的 `record.txt` 文件中提取。

CSV 文件的格式如下：
device_name, session_name, packet_distribution
其中：
- `device_name`：设备的名称。
- `session_name`：会话的标识符，包含设备信息和会话信息。
- `packet_distribution`：关键数据包的分布。

脚本的主要步骤如下：
1. 读取目标 CSV 文件 `uk_merged_results.csv`，每一行包含设备名、会话名和数据包分布。
2. 从 `session_name` 中提取会话标识符的前部分（即 `___` 前的部分）。
3. 根据 `device_name` 和提取的会话基本部分，查找 `source_dir` 中对应设备文件夹和会话文件夹。
4. 在找到的会话文件夹中读取 `record.txt` 文件，提取选择的周期值。
5. 更新 `session_name`，将提取的周期值添加到会话名的后面。
6. 将更新后的数据保存回 CSV 文件。

使用方法：
1. 修改 `target_csv` 和 `source_dir` 的路径为实际路径。
2. 运行脚本，它将更新 CSV 文件中的会话名。
"""

import os
import re
import csv


def extract_selected_cycle(record_file):
    """
    从 record.txt 文件中提取选择周期的值。
    """
    try:
        with open(record_file, 'r') as f:
            content = f.read()
            match = re.search(r"选择周期:\((\d+),", content)
            if match:
                return match.group(1)  # 提取选择周期数值
    except Exception as e:
        print(f"读取 {record_file} 时出错: {e}")
    return None


def update_session_name_in_csv(target_csv, source_dir):
    """
    更新 CSV 文件中的会话名，添加最佳周期值。
    """
    # 打开并读取CSV文件
    with open(target_csv, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    # 处理CSV文件中的每一行
    for i, row in enumerate(rows):
        if i == 0:  # 跳过第一行表头
            continue
        device_name, session_name, packet_distribution = row

        # 提取会话名中的前部分（即'___'前的内容）
        session_parts = session_name.split("___")
        session_base_name = session_parts[0]  # 提取会话的基本部分

        # 找到设备文件夹对应的 session 文件夹
        source_device_path = os.path.join(source_dir, device_name)
        if not os.path.isdir(source_device_path):
            print(f"设备文件夹 {device_name} 在 source_dir 中未找到，跳过。")
            continue

        # 在设备文件夹下寻找对应的会话文件夹
        session_path = None
        for root, dirs, _ in os.walk(source_device_path):
            for dir_name in dirs:
                if session_base_name in dir_name:
                    session_path = os.path.join(root, dir_name)
                    break
            if session_path:
                break

        # 如果找到了会话文件夹，读取record.txt，提取周期值
        if session_path:
            record_file = os.path.join(session_path, "record.txt")
            if os.path.isfile(record_file):
                selected_cycle = extract_selected_cycle(record_file)
                if selected_cycle:
                    # 更新会话名
                    new_session_name = f"{session_name}_____{selected_cycle}"
                    row[1] = new_session_name  # 更新 session_name 列
                    print(f"已更新会话名：{session_name} -> {new_session_name}")
            else:
                print(f"在 {session_path} 中找不到 record.txt 文件，跳过。")
        else:
            print(f"未找到对应的会话文件夹 {session_base_name}，跳过。")

    # 写回更新后的 CSV 文件
    with open(target_csv, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)
    print("CSV 文件更新完成！")


def main():
    target_csv = "artifact/outputs/signatures/14_keyPacketMerge/14_keyPacketMerge_merged_results.csv"
    source_dir = "artifact/outputs/signatures/3_selectDir"

    update_session_name_in_csv(target_csv, source_dir)


if __name__ == "__main__":
    main()
