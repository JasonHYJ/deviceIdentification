# -*- coding: utf-8 -*-

"""
测试代码：功能概述
该代码的主要功能是处理输入文件夹中的 CSV 文件，提取并清洗数据包负载（payload）中的多余零字符，
然后将结果保存为 TXT 文件，按照设备文件夹结构存储到输出文件夹中。
"""

import os
import pandas as pd
import re


def remove_excessive_zeros(payload):
    """
    删除负载中每一处超过10个连续零字符的部分。
    """
    if isinstance(payload, str):  # 检查payload是否为字符串类型
        return re.sub(r'0{11,}', '', payload)
    return payload  # 如果不是字符串，直接返回原始值


def process_csv_file(csv_file, output_file):
    """
    处理单个CSV文件，提取并处理每个数据包的负载，去除多余的零字符，并保存到输出文件。
    """
    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 提取并处理每个数据包的负载
    payloads = []
    for _, row in df.iterrows():
        payload = row['payload']
        if isinstance(payload, str) and payload:  # 确保负载是字符串并且非空
            cleaned_payload = remove_excessive_zeros(payload)  # 处理负载
            payloads.append(cleaned_payload)
        else:
            # 如果payload是NaN或空值，可以跳过或者替换为空字符串
            payloads.append('')  # 这里使用空字符串作为默认值

    # 保存处理后的负载到txt文件
    with open(output_file, 'w') as f:
        for payload in payloads:
            f.write(str(payload) + '\n')  # 确保每个负载是字符串类型，进行拼接
            f.write('\n')  # 每个负载后添加一个空行

    print(f"处理后的负载已保存到: {output_file}")


def process_device_data(input_folder, output_folder):
    """
    遍历输入文件夹，处理每个设备文件夹中的CSV文件，并保存到输出文件夹。
    """
    # 使用os.walk遍历输入文件夹，获取所有子目录和文件
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.csv'):
                # 获取当前CSV文件的路径
                csv_path = os.path.join(root, file)

                # 生成输出文件的路径
                relative_path = os.path.relpath(root, input_folder)  # 获取设备文件夹相对路径
                output_dir = os.path.join(output_folder, relative_path)  # 在输出文件夹中创建相应的设备文件夹
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # 生成输出的TXT文件路径
                output_txt_file = os.path.splitext(file)[0] + '.txt'  # 使用CSV文件名生成TXT文件
                output_path = os.path.join(output_dir, output_txt_file)

                # 处理CSV文件并保存到目标路径
                process_csv_file(csv_path, output_path)


def main():
    # 输入和输出文件夹路径
    input_folder = '/home/hyj/deviceIdentification/dataset/MonIoTr/15_keyPacketFeature/uk'  # 总文件夹uk
    output_folder = '/home/hyj/deviceIdentification/dataset/testData/payloadTxt/uk'  # 输出文件夹new_uk

    # 开始处理
    process_device_data(input_folder, output_folder)
    print("所有文件处理完成！")


if __name__ == "__main__":
    main()
