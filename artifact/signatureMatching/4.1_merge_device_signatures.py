# -*— coding: utf-8 -*-

"""
将所有签名合并到一个文件中，以设备-会话-关键数据包特征签名的形式进行保存.
1、使用 os.walk 遍历文件夹，收集每个设备文件夹中的会话 CSV 文件内容。
2、每个会话的签名内容被转化为字典列表（特征矩阵的每行对应一个字典）。签名矩阵被序列化为 JSON 字符串存储在 signature 列中。
3、将收集到的设备名、会话名和签名信息保存到一个 CSV 文件中。

1. 遍历设备文件夹：
    使用 os.walk 遍历输入目录中的所有设备文件夹及其会话文件夹。
2. 收集签名矩阵：
    从每个会话的 CSV 文件中读取关键数据包的签名矩阵，将其转化为字典列表，并存储设备名、会话名及签名信息。
3. 序列化签名矩阵：
    将签名矩阵序列化为 JSON 字符串，便于在 CSV 文件中保存。
4. 保存为合并文件：
    将所有设备和会话的签名数据保存到指定路径下的合并 CSV 文件中，字段包括 device_name, session_name 和 signature。
5. 统计处理信息：
    输出已处理的 CSV 文件数量，以及保存后的合并文件路径。
"""

import os
import pandas as pd
import json


def collect_signatures(input_dir):
    """
    遍历输入目录，收集所有设备的会话签名。

    Args:
        input_dir (str): 输入的总文件夹路径。

    Returns:
        list: 包含每个设备、会话和签名矩阵的列表。
    """
    data = []  # 用于存储最终的设备、会话和签名信息
    file_count = 0  # 初始化计数器

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.csv'):
                file_count += 1  # 每处理一个文件，计数器加 1
                device_name = os.path.basename(root)  # 获取设备文件夹名
                session_name = file  # 会话名即文件名
                file_path = os.path.join(root, file)

                # 打印当前正在处理的文件
                print(f"正在处理文件：{file_path}")

                # 读取会话的签名矩阵
                try:
                    df = pd.read_csv(file_path)
                    signature_matrix = df.to_dict(orient='records')  # 转换为列表形式

                    # 存储设备名、会话名和签名
                    data.append({
                        'device_name': device_name,
                        'session_name': session_name,
                        'signature': signature_matrix
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    print(f"目录遍历完成，共处理了 {file_count} 个文件，签名收集完毕。")
    return data


def save_to_csv(data, output_file):
    """
    将收集到的数据保存为 CSV 文件。

    Args:
        data (list): 包含设备、会话和签名信息的列表。
        output_file (str): 输出 CSV 文件路径。
    """

    print(f"开始保存数据到文件：{output_file}")

    # 创建 DataFrame
    output_df = pd.DataFrame(data)

    # 将签名矩阵转换为 JSON 字符串以便保存
    output_df['signature'] = output_df['signature'].apply(json.dumps)

    # 保存为 CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # 确保输出目录存在
    output_df.to_csv(output_file, index=False, encoding='utf-8')


def main():
    input_dir = "artifact/outputs/signatures/16_keyPacketSignatureWithLSH"  # 输入的总文件夹路径
    output_dir = "artifact/outputs/merged_signatures/17_signatureMerge"  # 新的输出目录
    # output_dir = '/home/hyj/deviceIdentification/dataset/test/us'

    # 提取输入路径的最后一层目录名
    last_dir_name = os.path.basename(os.path.normpath(input_dir))  # 获取最后一层目录名，如 "uk"
    output_file = os.path.join(output_dir, f"{last_dir_name}_merged_signatures.csv")  # 输出文件路径

    print("开始收集签名数据...")
    data = collect_signatures(input_dir)

    print(f"开始保存合并后的签名数据...")
    save_to_csv(data, output_file)

    print("程序运行结束！")


if __name__ == "__main__":
    main()
