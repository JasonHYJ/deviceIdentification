# -- coding: utf-8 --
"""
本文件对每个csv文件进行处理，从里面提取出特定列用于构建特征向量，
包含['frame.time_epoch', 'frame.len', 'direction', 'time_interval', 'protocol_type', 'payload', 'label']
将协议类型列只是用tcp或udp进行表示，然后将对应的payload保存成新列，并且使用会话文件名作为label。
处理后的数据保存到一个新的目录中，并保留原始文件的目录结构。

1. 列的选择与特征构建
    提取列：['frame.time_epoch', 'frame.len', 'direction', 'time_interval']。
    根据 frame.protocols 列，将协议类型映射为 tcp、udp、dhcp 或 unknown。
    根据协议类型提取对应的 tcp.payload 或 udp.payload，保存到新列 payload。
2. 添加标签列
    使用 CSV 文件所在的会话文件夹名称作为 label。
3. 目录结构与文件保存
    保留原始 CSV 文件的目录结构。
    处理后的 CSV 文件保存到指定的新目录。
4. 遍历与处理
    遍历源文件夹中的所有 CSV 文件，对每个文件进行特征提取。
    将处理后的结果保存到目标目录。
5. 输出进度与统计
    处理每个文件时打印保存路径。
    统计并输出总共处理的文件数量。
"""

import os
import pandas as pd


def process_csv_file(csv_file, new_directory, root_directory):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)

    # 提取相关列
    df_filtered = df[['frame.time_epoch', 'frame.len', 'direction', 'time_interval']].copy()

    # 创建新的列来保存协议类型和有效负载
    df_filtered['protocol_type'] = df['frame.protocols'].apply(
        lambda x: 'dhcp' if 'dhcp' in x else ('tcp' if 'tcp' in x else ('udp' if 'udp' in x else 'unknown')))

    df_filtered['payload'] = df_filtered.apply(
        lambda row: df.loc[row.name, 'udp.payload'] if row['protocol_type'] == 'dhcp'  # 如果是dhcp，从udp.payload提取
        else (df.loc[row.name, 'tcp.payload'] if row['protocol_type'] == 'tcp'
              else (df.loc[row.name, 'udp.payload'] if row['protocol_type'] == 'udp' else None)), axis=1)

    # 获取会话文件夹名作为标签
    session_folder_name = os.path.basename(os.path.dirname(csv_file))

    # 添加标签列
    df_filtered['label'] = session_folder_name

    # 计算 CSV 文件相对路径
    relative_path = os.path.relpath(csv_file, root_directory)

    # 新的保存路径
    new_csv_path = os.path.join(new_directory, relative_path)

    # 确保保存路径的目录存在
    os.makedirs(os.path.dirname(new_csv_path), exist_ok=True)

    # 保存处理后的文件
    df_filtered.to_csv(new_csv_path, index=False)
    print(f"Processed and saved: {new_csv_path}")


def traverse_and_process(root_directory, new_directory):
    # 文件计数器
    file_count = 0

    # 遍历所有文件夹，处理每个 CSV 文件
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".csv"):
                csv_file_path = os.path.join(root, file)
                process_csv_file(csv_file_path, new_directory, root_directory)
                file_count += 1  # 每处理一个文件，计数器加1

    # 打印总共处理的文件数量
    print(f"Total files processed: {file_count}")


if __name__ == "__main__":
    root_directory = "artifact/outputs/preproc/8_csvSelect"  # 原始文件夹路径
    new_directory = "artifact/outputs/preproc/9_feature"  # 新文件夹路径
    # new_directory = "/home/hyj/deviceIdentification/dataset/test/uk"

    # 开始处理并将文件保存到新目录下
    traverse_and_process(root_directory, new_directory)
