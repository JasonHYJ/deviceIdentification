# -- coding: utf-8 --

"""
将同一个会话文件夹中的所有 CSV 文件合并成一个 CSV 文件，并将合并后的文件保存到指定的目标文件夹。
每个合并后的文件包含该会话所有样本的数据包特征信息，适用于后续的聚类操作。
代码会遍历设备文件夹中的所有会话文件夹，并将每个会话文件夹中的 CSV 文件合并后保存。

1. 会话文件夹的识别与遍历
    遍历设备文件夹中的所有会话文件夹。
    判断会话文件夹中是否包含 CSV 文件。
2. CSV 文件的合并
    读取会话文件夹中的所有 CSV 文件。
    将 CSV 文件的数据合并为一个 Pandas DataFrame。
    将合并后的数据保存到目标目录，文件名格式为：{会话文件夹名}___{CSV文件数}.csv。
3. 目录结构的保留
    在目标目录中创建与设备文件夹对应的子文件夹。
    保持设备-会话的层级结构。
4. 统计与输出
    统计每个会话文件夹中处理的 CSV 文件数量。
    输出合并文件的保存路径及总处理进度，包括总会话数、总 CSV 文件数、生成的合并文件数。
"""

import os
import pandas as pd


def merge_csv_files_in_session(session_folder, output_file):
    # 获取会话文件夹中的所有 CSV 文件
    csv_files = [f for f in os.listdir(session_folder) if f.endswith('.csv')]

    # 用于存储所有 CSV 文件的数据
    merged_data = []

    for csv_file in csv_files:
        csv_path = os.path.join(session_folder, csv_file)
        # 读取 CSV 文件
        data = pd.read_csv(csv_path)
        # 将数据追加到合并数据列表中
        merged_data.append(data)

    # 合并所有 CSV 文件的数据，只保留一个表头
    merged_df = pd.concat(merged_data, ignore_index=True)

    # 保存合并后的数据到新的 CSV 文件
    merged_df.to_csv(output_file, index=False)
    print(f"Saved merged file to {output_file}")

    # 返回处理的 CSV 文件数量
    return len(csv_files)


def process_all_sessions(src_folder, dst_folder):
    total_csv_files = 0
    total_sessions = 0
    total_merged_files = 0

    # 遍历设备文件夹
    for root, dirs, files in os.walk(src_folder):
        for sub_dir in dirs:
            session_folder = os.path.join(root, sub_dir)
            # 如果是会话文件夹，合并所有 CSV 文件
            if any(f.endswith('.csv') for f in os.listdir(session_folder) if isinstance(f, str)):   # isinstance，用于检查一个对象是否属于指定的类或类型（包括其子类）。
                total_sessions += 1

                # 获取设备文件夹路径
                # 如果session_folder中有csv文件，那个sub_dir就是当前会话文件夹，dirs就是当前的会话文件夹列表集合，root就是当前子文件夹，所以dirname返回上一层文件夹路径就是设备文件夹
                device_folder = os.path.dirname(root)
                device_name = os.path.basename(device_folder)

                # 统计会话文件夹中的 CSV 文件数量
                csv_count = len([f for f in os.listdir(session_folder) if isinstance(f, str) if f.endswith('.csv')])

                # 生成输出文件名，以会话文件夹名称命名
                session_name = os.path.basename(session_folder)
                output_file = os.path.join(dst_folder, device_name, f"{session_name}___{csv_count}.csv")

                # 创建设备文件夹
                os.makedirs(os.path.join(dst_folder, device_name), exist_ok=True)

                # 合并并保存 CSV 文件，统计合并的 CSV 文件数量
                merged_csv_count = merge_csv_files_in_session(session_folder, output_file)
                total_csv_files += merged_csv_count
                total_merged_files += 1

                # 输出当前处理信息
                print(f"Processed session: {session_name} from {device_name}, merged { merged_csv_count} CSV files.")

    # 最终统计信息
    print(f"\nTotal sessions processed: {total_sessions}")
    print(f"Total CSV files processed: {total_csv_files}")
    print(f"Total merged CSV files generated: {total_merged_files}")


if __name__ == "__main__":
    src_folder = "/home/hyj/deviceIdentification/dataset/LabData/9_feature"  # 替换为源文件夹路径
    dst_folder = "/home/hyj/deviceIdentification/dataset/LabData/10_featureMerge"  # 替换为目标文件夹路径
    # dst_folder = "/home/hyj/deviceIdentification/dataset/test/uk"
    process_all_sessions(src_folder, dst_folder)
