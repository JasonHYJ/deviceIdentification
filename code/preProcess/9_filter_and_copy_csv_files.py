# -*- coding: utf-8 -*-

"""
将原目录下的所有文件复制到新路径下，保留目录结构，并在新路径下进行过滤处理。
实现的功能：
1、复制文件及其目录结构：将一个源文件夹中所有以 .csv 结尾的文件，按照原目录结构复制到一个目标文件夹。
2、过滤并处理 CSV 文件：在目标文件夹中，对每个 CSV 文件进行过滤：
    删除文件名为 noise_samples.csv 的文件。
    根据文件夹名称中的样本数量，检查 CSV 文件的行数（特征向量数目），如果小于特定阈值，就删除文件。

1. 文件复制与目录结构保留
    遍历源文件夹，复制所有以 .csv 结尾的文件到目标文件夹。
    复制时保留原始目录结构。
2. 文件过滤规则
    如果文件名为 noise_samples.csv，直接删除。
    从会话文件夹名称中提取样本总数。
    检查每个 CSV 文件的行数（特征向量数目）。如果行数少于样本总数的一半，删除文件。
3. 输出统计信息
    打印每个文件的处理信息，包括路径、特征向量数目和是否被删除。
    最后统计并输出总处理的 CSV 文件数和删除的文件数。
"""

import os
import shutil
import pandas as pd


# 复制文件及其目录结构
def copy_files_with_structure(source_folder, target_folder):
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.csv'):
                # 构建源文件路径
                source_file_path = os.path.join(root, file)

                # 计算目标文件路径
                relative_path = os.path.relpath(root, source_folder)  # 获取相对路径
                target_dir_path = os.path.join(target_folder, relative_path)  # 构建新的目标文件夹路径

                # 如果目标文件夹不存在，创建它
                if not os.path.exists(target_dir_path):
                    os.makedirs(target_dir_path)

                # 构建目标文件路径
                target_file_path = os.path.join(target_dir_path, file)

                # 复制文件到目标路径
                shutil.copy2(source_file_path, target_file_path)
                print(f"Copied {source_file_path} to {target_file_path}")


# 过滤处理 CSV 文件，删除不符合条件的文件
def process_csv_files(root_folder):
    total_files = 0
    deleted_files = 0

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.csv'):
                total_files += 1
                file_path = os.path.join(root, file)

                # 如果文件名是 noise_samples.csv，直接删除
                if file == 'noise_samples.csv':
                    print('*')
                    print(f"Deleting noise_samples.csv at {file_path}")
                    print()
                    os.remove(file_path)
                    deleted_files += 1
                    continue  # 跳过之后的处理逻辑

                # 从文件路径中获取会话文件夹名称的最后一部分（假设是样本数目）
                session_folder = os.path.basename(root)  # 获取会话文件夹名称
                sample_count = int(session_folder.split('___')[-1])  # 假设最后一部分是样本数

                # 读取 CSV 文件
                df = pd.read_csv(file_path)
                vector_count = len(df)  # 获取特征向量的行数

                # 打印文件信息
                print(f"Processing {file_path}... Vector count: {vector_count}, Required: {sample_count / 2}")

                # 如果特征向量数目小于 (样本数目 / 2)，删除文件。说明该数据包并不存在于大部分样本中，所需的数据包应该是起码在大部分的样本中都出现1次或者多次的
                if vector_count < (sample_count / 2):
                    print(f"Deleting {file_path}")
                    os.remove(file_path)
                    deleted_files += 1

                print()

    return total_files, deleted_files


def main():
    # 设置源文件夹和目标文件夹路径
    source_folder = '/home/hyj/deviceIdentification/dataset/LabData/11_featureCluster'
    target_folder = '/home/hyj/deviceIdentification/dataset/LabData/12_featureClusterFilter'

    # source_folder = '/home/hyj/deviceIdentification/dataset/test/us'
    # target_folder = '/home/hyj/deviceIdentification/dataset/test1/us'

    # 复制文件到目标路径，并保留目录结构
    print(f"Copying files from {source_folder} to {target_folder}...")
    copy_files_with_structure(source_folder, target_folder)

    # 开始在新的路径下处理 CSV 文件9
    print(f"Starting to process CSV files in {target_folder}...")
    total_files, deleted_files = process_csv_files(target_folder)

    # 打印处理结果
    print(f"Total CSV files processed: {total_files}")
    print(f"Total CSV files deleted: {deleted_files}")


if __name__ == "__main__":
    main()

