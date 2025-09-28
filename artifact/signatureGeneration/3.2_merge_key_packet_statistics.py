# -*- coding: utf-8 -*-

"""
该文件将上一步得到的每个设备的会话中的关键数据包的出现次数统计情况进行合并，合并成一个csv文件。
相当于在外面添加一层设备名的嵌套

1. 遍历设备目录
    从指定路径中查找每个设备的统计 CSV 文件。
    读取文件，提取会话名称和关键数据包分布信息。
2. 数据存储与合并
    使用嵌套字典结构 all_devices_data 组织数据：
        一级键为设备名称。
        二级键为会话名称。
        值为关键数据包的分布统计。
3. 结果保存
    合并所有设备的统计结果。
    生成统一的 CSV 文件，格式如下：
        device_name,session_name,packet_distribution
        device1,session1,{'size1_direction1': count1, 'size2_direction2': count2, ...}
        device1,session2,{'size1_direction1': count1, 'size2_direction2': count2, ...}
        ...
    输出文件命名为 {output_dir}_merged_results.csv，保存在指定输出目录中。
4. 输出文件检查
    如果输出文件已存在，跳过写入操作，避免覆盖。
"""

import os
import csv
import pandas as pd
from collections import defaultdict

def merge_device_csvs(root_dir, output_dir):
    all_devices_data = defaultdict(dict)  # 存储所有设备的数据

    # 遍历所有设备的 CSV 文件
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".csv"):
                device_name = os.path.splitext(file)[0]  # 设备名称
                csv_path = os.path.join(root, file)
                print(f"处理设备: {device_name} 的文件: {csv_path}")

                # 读取设备的 CSV 文件
                df = pd.read_csv(csv_path)

                # 将会话和对应的数据包分布添加到字典中
                for _, row in df.iterrows():
                    session_name = row['session_name']
                    packet_distribution = row['packet_distribution']
                    all_devices_data[device_name][session_name] = eval(packet_distribution)  # 将字符串转换为字典

                print(f"完成处理设备: {device_name} 的文件.")

    # 检查输出目录是否存在，如果不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"输出目录 {output_dir} 创建成功。")

    # 提取output_dir的最后一层目录名称，并用其命名输出文件
    dir_name = os.path.basename(output_dir.rstrip(os.sep))  # 获取输出目录的最后一部分（去除结尾的分隔符）
    output_file = os.path.join(output_dir, f"{dir_name}_merged_results.csv")  # 生成合并结果文件名

    # 如果输出文件不存在，则创建文件并写入
    if not os.path.exists(output_file):
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['device_name', 'session_name', 'packet_distribution'])  # 写入表头

            # 将合并的数据写入 CSV 文件
            for device_name, sessions in all_devices_data.items():
                for session_name, distribution in sessions.items():
                    writer.writerow([device_name, session_name, distribution])

        print(f"所有设备的统计结果已合并并保存到 {output_file}")
    else:
        print(f"文件 {output_file} 已存在，跳过保存.")


# 主函数入口
if __name__ == "__main__":
    input_dir = "artifact/outputs/signatures/13_keyPacketStatistics"  # 替换为设备 CSV 文件的路径
    output_dir = "artifact/outputs/signatures/14_keyPacketMerge"  # 替换为输出文件夹路径

    # input_dir = '/home/hyj/deviceIdentification/dataset/test/us'
    # output_file = '/home/hyj/deviceIdentification/dataset/test1/us/us_merged_results.csv'

    merge_device_csvs(input_dir, output_dir)
