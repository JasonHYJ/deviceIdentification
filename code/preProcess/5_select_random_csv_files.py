# -- coding: utf-8 --
"""
本文件从每个会话文件中选取50个csv文件，并且保存到新目录下。少于50个的全选，多于50个的随机选取50个
实现的功能：
从每个会话文件夹中选取一定数量的 CSV 文件（默认是 50 个），并将它们复制到新的目标目录下，同时保留原始文件夹的结构。
如果会话文件夹中的 CSV 文件少于 50 个，则全部复制；如果多于 50 个，则随机选取 50 个。

1. 遍历源文件夹
    遍历源目录中的所有子目录，识别包含 CSV 文件的会话文件夹。
2. 随机选择文件
    如果会话文件夹中的 CSV 文件少于或等于指定数量（默认 50 个），则全部复制。
    如果多于指定数量，则随机选取指定数量的文件。
3. 复制文件并保留目录结构
    创建目标文件夹，保持原始目录结构。
    将选定的文件复制到目标目录中。
4. 统计与进度输出
    记录总共复制的文件数。
    在处理过程中打印每个文件的复制路径。
    最后输出总计复制的文件数。
"""

import os
import random
import shutil


def copy_random_csv_files(src_folder, dst_folder, num_files=50):   # 初始默认是50个，我现在希望能够多一些样本，这样一些数据包在聚类时候可能被保留
    total_copied_files = 0  # 初始化计数器
    for root, dirs, files in os.walk(src_folder):
        # 检查当前路径是否是会话文件夹（根据CSV文件存在与否判断）
        csv_files = [f for f in files if f.endswith('.csv')]
        if csv_files:
            # 计算目标路径，以保持原始文件结构
            relative_path = os.path.relpath(root, src_folder)
            target_session_path = os.path.join(dst_folder, relative_path)

            # 创建目标文件夹（保持与原文件夹一致的结构）
            os.makedirs(target_session_path, exist_ok=True)

            # 随机选择文件
            selected_files = csv_files if len(csv_files) <= num_files else random.sample(csv_files, num_files)

            # 复制选定的文件到目标文件夹
            for csv_file in selected_files:
                src_file = os.path.join(root, csv_file)
                dst_file = os.path.join(target_session_path, csv_file)
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")
                total_copied_files += 1  # 更新计数器

    print(f"Total files copied: {total_copied_files}")  # 输出总计数


if __name__ == "__main__":
    src_folder = "/home/hyj/deviceIdentification/dataset/LabData/7_csvFilter"  # 替换为你的总文件夹路径
    dst_folder = "/home/hyj/deviceIdentification/dataset/LabData/8_csvSelect"  # 替换为目标文件夹路径
    copy_random_csv_files(src_folder, dst_folder)
