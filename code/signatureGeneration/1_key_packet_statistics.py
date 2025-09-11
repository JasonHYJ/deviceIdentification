# -*— coding: utf-8 -*-

"""
该文件用于确认每个设备的每个会话中的关键数据包的情况，关键数据包的大小是多少？方向是什么？在每个样本中出现多少次？统计整理出来
每个设备文件整理出一个二维字典进行保存，即{'会话1': {'size1':100, 'size2': 200,...}, '会话2': {size1:10, size2: 20},...}
构建的字典保存到新的目录结构下，以csv文件的格式

1. 设备与会话的遍历
    使用 os.walk 遍历设备目录及其会话文件夹。
    读取每个会话文件夹中的 CSV 文件。
2. 关键数据包统计
    根据 frame.len（数据包大小）和 direction（方向）分组，统计其出现次数。
    找出出现次数最多的 (frame.len, direction) 组合，计算其平均每个样本的出现次数。
3. 数据处理与存储
    将统计结果存储为一个二维字典，结构如下：
        {'设备名': {'会话名': {(size, direction): avg_count_per_sample}}}。
        将结果导出为 CSV 文件，保存在目标路径。
4. 结果保存
    每个设备的统计结果保存为独立的 CSV 文件，格式如下：
        session_name,packet_distribution
        session1,"{'size1_direction1': count1, 'size2_direction2': count2, ...}"
        session2,"{'size1_direction1': count1, 'size2_direction2': count2, ...}"
"""

import os
import csv
import pandas as pd
from collections import defaultdict


# 统计每个设备的聚类情况
def process_device_folders(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    device_results = defaultdict(lambda: defaultdict(dict))  # 存储所有设备的聚类结果

    # 使用 os.walk 遍历设备和会话文件夹
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".csv"):
                session_folder = os.path.basename(root)  # 会话文件夹名
                device_folder = os.path.basename(os.path.dirname(root))  # 设备文件夹名

                # 从会话文件夹名提取样本数
                try:
                    num_samples = int(session_folder.split('___')[-1])
                    print(f"会话: {session_folder}, 样本数: {num_samples}")
                except ValueError:
                    num_samples = 50  # 默认值
                    print(f"会话: {session_folder}, 样本数解析失败，使用默认值: {num_samples}")

                csv_path = os.path.join(root, file)
                print(f"处理文件: {csv_path}")

                # 读取csv文件
                df = pd.read_csv(csv_path)

                # 统计 (frame.len, direction) 的出现次数
                size_direction_counts = df.groupby(['frame.len', 'direction']).size()

                if size_direction_counts.empty:
                    print(f"警告: {csv_path} 中没有可用的数据包。")
                    continue

                # 选择出现次数最多的数据包大小和方向
                most_common = size_direction_counts.idxmax()
                most_common_size = most_common[0]
                most_common_direction = most_common[1]
                most_common_count = size_direction_counts.max()

                # 计算整除和余数
                quotient = most_common_count // num_samples
                remainder = most_common_count % num_samples

                # 根据余数决定向上或向下取整
                if remainder >= (num_samples / 2):
                    avg_count_per_sample = quotient + 1  # 向上取整，如果余数在一半以上样本中的话，认为余数也算一个关键数据包
                else:
                    avg_count_per_sample = quotient  # 向下取整

                print(f"数据包大小: {most_common_size}, 方向: {most_common_direction}, "
                      f"出现次数: {most_common_count}, 每个样本中的平均出现数: {avg_count_per_sample}")

                # 将结果存储到字典
                device_results[device_folder][session_folder][
                    (most_common_size, most_common_direction)] = avg_count_per_sample

    # 保存每个设备的统计结果到新的CSV文件中
    for device_name, sessions in device_results.items():
        print(f"保存设备: {device_name} 的统计结果")
        save_results_to_csv(sessions, output_dir, device_name)


# 保存统计结果到CSV文件
def save_results_to_csv(device_results, output_dir, device_name):
    output_file = os.path.join(output_dir, f"{device_name}.csv")
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['session_name', 'packet_distribution'])

        for session, distribution in device_results.items():
            # 将 (size, direction) 转换为字典形式
            distribution_dict = {f"{size}_{direction}": count for (size, direction), count in distribution.items()}
            writer.writerow([session, distribution_dict])

    print(f"设备: {device_name} 的统计结果已保存到 {output_file}")


# 主函数入口
if __name__ == "__main__":
    root_dir = "/home/hyj/deviceIdentification/dataset/LabData/12_featureClusterFilter"  # 替换为你的设备总文件夹路径
    output_dir = "/home/hyj/deviceIdentification/dataset/LabData/13_keyPacketStatistics"  # 替换为输出文件夹路径

    # root_dir = '/home/hyj/deviceIdentification/dataset/test1/us'
    # output_dir = '/home/hyj/deviceIdentification/dataset/test/us'

    process_device_folders(root_dir, output_dir)
