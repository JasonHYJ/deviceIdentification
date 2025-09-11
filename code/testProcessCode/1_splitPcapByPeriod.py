# -*— coding: utf-8 -*-

"""
对于每个设备待测试的pcap文件，先根据该设备的最大周期进行pcap文件的划分。
"""

import os
import pandas as pd
import re

from scapy.layers.l2 import Ether
from scapy.utils import PcapReader, PcapWriter


def get_device_max_period(signature_csv_path):
    """
    从签名CSV文件中提取每个设备的最大周期。

    Args:
        signature_csv_path (str): 签名文件路径。

    Returns:
        dict: 每个设备的最大周期，格式为 {device_name: max_period}。
    """
    print(f"读取签名文件：{signature_csv_path}")
    # 读取CSV文件
    df = pd.read_csv(signature_csv_path)

    # 提取周期信息
    df['period'] = df['session_name'].apply(lambda x: int(re.search(r'_____(\d+)', x).group(1)))

    # 获取每个设备的最大周期
    max_periods = df.groupby('device_name')['period'].max().to_dict()
    print("已提取设备最大周期：", max_periods)
    return max_periods


def split_pcap_by_period(pcap_file, output_dir, max_period):
    """
    按照最大周期将PCAP文件切分为多个部分。

    Args:
        pcap_file (str): PCAP文件路径。
        output_dir (str): 切分后的文件保存目录。
        max_period (int): 最大周期（单位：秒）。
    """
    print(f"开始切分PCAP文件：{pcap_file}, 最大周期：{max_period} 秒")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    part_count = 1
    current_time = None
    writer = None

    with PcapReader(pcap_file) as reader:
        for packet in reader:
            # 获取数据包的时间戳
            packet_time = float(packet.time)

            # 初始化或开始新的时间窗口
            if current_time is None or packet_time - current_time >= max_period:
                # 如果有打开的文件，先关闭它
                if writer:
                    writer.close()

                # 打开新的PCAP文件写入
                output_file = os.path.join(output_dir, f"part{part_count}.pcap")
                writer = PcapWriter(output_file, append=False, linktype=1)  # 设置链路层类型为 Ethernet
                print(f"创建新PCAP文件：{output_file}")

                part_count += 1
                current_time = packet_time

            # 修复链路层类型不一致的问题
            try:
                if not isinstance(packet, Ether):
                    packet = Ether() / packet
            except Exception as e:
                print(f"跳过无法处理的数据包：{e}")
                continue

            # 写入当前数据包
            writer.write(packet)

        # 关闭最后一个文件
        if writer:
            writer.close()
    print(f"PCAP文件切分完成，共生成 {part_count - 1} 个部分。")


def main():
    # 输入参数
    signature_csv_path = "/home/hyj/deviceIdentification/dataset/LabData/14_keyPacketMerge/14_keyPacketMerge_merged_results.csv"  # 签名集合CSV文件路径
    input_dir = "/home/hyj/deviceIdentification/dataset/testData/LabData/originalSingleData"  # 包含设备PCAP文件的目录
    output_dir = "/home/hyj/deviceIdentification/dataset/testData/LabData/splitByPeriod"  # 切分后的PCAP文件保存路径

    print("程序开始运行...")

    # 获取每个设备的最大周期
    max_periods = get_device_max_period(signature_csv_path)

    # 遍历设备文件夹
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.pcap'):  # 只处理PCAP文件
                device_name = os.path.basename(root)  # 获取设备名
                if device_name in max_periods:
                    max_period = max_periods[device_name] * 2
                    pcap_file = os.path.join(root, file)
                    device_output_dir = os.path.join(output_dir, device_name)

                    # 切分PCAP文件
                    split_pcap_by_period(pcap_file, device_output_dir, max_period)
                else:
                    print(f"警告：未找到设备 {device_name} 的最大周期，跳过文件 {file}")

    print("程序运行结束！")


if __name__ == "__main__":
    main()
