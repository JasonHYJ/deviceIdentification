# -*- coding: utf-8 -*-

"""
功能说明：
本脚本用于处理CSV格式的网络流量数据，包含以下三个主要步骤：

1. 复制CSV文件及目录结构
    - 将源目录下的所有CSV文件和子目录完整复制到目标目录（保留原有结构）。

2. 过滤CSV文件内容
    - 遍历目标目录下的每一个CSV文件，根据以下规则筛选保留的数据包：
        a. TLS 应用数据包（tls.record.content_type == 23）
        b. 有效 TCP 数据包（tcp.len ≠ 0 且不包含 tls 协议）
        c. TLS 握手数据包（frame.protocols 包含 tls 且 tls.record.content_type 为空）
        d. UDP 数据包（frame.protocols 包含 udp）
    - 对于过滤后为空的CSV文件，直接删除。

3. 清理CSV数量不足的目录
    - 每个文件夹过滤完所有CSV文件后，检查剩余的CSV文件数量。
    - 若剩余CSV文件数量少于15个，则删除整个文件夹；否则保留该文件夹。

4. 输出进度与统计
    - 实时打印每个文件的处理状态与最终统计结果。
"""

# -*- coding: utf-8 -*-

import os
import shutil
import pandas as pd


def copy_directory(src_folder, dst_folder):
    """
    复制整个 CSV 文件目录及其内容到目标目录
    """
    for root, dirs, files in os.walk(src_folder):
        # 计算相对路径以保留目录结构
        rel_path = os.path.relpath(root, src_folder)
        dst_path = os.path.join(dst_folder, rel_path)

        # 创建目标目录结构
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        # 复制文件
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_path, file)
            shutil.copy2(src_file, dst_file)
            print(f"Copied: {src_file} -> {dst_file}")


def filter_csv_files(input_dir):
    """
    过滤指定目录下的所有 CSV 文件，删除无关协议的数据包，并保存过滤后的数据。
    """
    # 统计处理的文件数量
    processed_files_count = 0

    # 遍历指定目录中的所有 CSV 文件
    for root, dirs, files in os.walk(input_dir, topdown=False):
        # 获取本目录中的CSV文件
        csv_files = [f for f in files if f.endswith('.csv')]

        # === 对CSV文件进行过滤 ===
        for name in csv_files:
            filename = os.path.join(root, name)
            print(f"Processing file: {filename}")

            # 读取 CSV 文件
            df = pd.read_csv(filename, encoding='utf-8', header=0, keep_default_na=False)

            # 设置 pandas 的显示选项
            pd.set_option('expand_frame_repr', False)  # 完整打印所有输出行内容
            pd.set_option('display.max_columns', None)  # 显示所有列
            pd.set_option('display.max_rows', None)  # 显示所有行

            # 过滤有效的数据包内容信息
            condition1 = (df['tls.record.content_type'] == '23') | (df['tls.record.content_type'] == '23.0')    # TLS 数据包，内容类型为 23
            condition2 = (df['tcp.len'] != 0) & (df['tcp.len'] != '0.0') & (~df['frame.protocols'].str.contains('tls'))  # 有效 TCP 数据包
            condition3 = df['frame.protocols'].str.contains('tls') & (df['tls.record.content_type'] == '')  # TLS 握手阶段数据包
            # 新增条件：保留 UDP 数据包
            condition_udp = df['frame.protocols'].str.contains('udp', na=False)

            # 合并过滤结果
            result = df[condition1 | condition2 | condition3 | condition_udp]

            # 如果结果为空，删除 CSV 文件，否则保存结果
            if result.empty:
                os.remove(filename)
                print(f"Deleted empty file: {filename}")
            else:
                result.to_csv(filename, index=False)
                print(f"Saved filtered file: {filename}")

            # 计数已处理文件
            processed_files_count += 1
            print(f"Processed files count: {processed_files_count}")

        # 此处只判断“会话文件夹”（即root）中剩余CSV文件数量
        if csv_files:  # 防止刚好被删了
            remaining_csv = [f for f in os.listdir(root) if f.endswith('.csv')]
            if len(remaining_csv) < 15:
                shutil.rmtree(root)
                print(f"Deleted session folder (too few CSV files): {root}")
            else:
                print(f"Retained session folder: {root}")

    # 最终输出总共处理的文件数
    print(f"Total processed CSV files: {processed_files_count}")


def main():
    # 定义源文件夹路径和目标文件夹路径
    src_folder = '/home/hyj/deviceIdentification/dataset/LabData/6_csvAddTime'  # 原始 CSV 文件目录
    dst_folder = '/home/hyj/deviceIdentification/dataset/LabData/7_csvFilter'  # 复制后的 CSV 文件目录

    # 复制文件目录\
    copy_directory(src_folder, dst_folder)

    # 对复制后的目录进行 CSV 文件过滤
    filter_csv_files(dst_folder)


if __name__ == "__main__":
    main()
