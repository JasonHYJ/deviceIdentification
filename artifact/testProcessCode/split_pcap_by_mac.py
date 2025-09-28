"""
脚本名称: split_pcap_by_mac.py

功能:
该脚本用于解析指定文件夹中的 pcap 流量文件，并按照 IoT 设备的 MAC 地址拆分流量。
对于每个 pcap 文件，提取属于各个设备的数据包，并单独存储到相应的文件夹中。
如果某设备在某天没有流量，则不会生成相应的 pcap 文件。

过程:
1. 遍历输入文件夹中的所有 pcap 文件。
2. 逐步读取每个 pcap 文件（使用流式读取方式处理大文件，避免内存溢出）。
3. 若该 MAC 地址在 pcap 文件中出现，则提取相关数据包，并存储到 "设备名_日期.pcap" 文件。
4. 若 MAC 地址未出现，则跳过该设备，不生成 pcap 文件。
5. 每个设备的 pcap 文件存入对应的文件夹 ("DeviceA/", "DeviceB/" 等)。

"""

import os
import glob
from scapy.all import PcapReader, wrpcap


def extract_device_packets(input_pcap, mac_address):
    """使用流式读取方式提取指定MAC地址的流量，避免内存溢出"""
    print(f"正在处理文件: {input_pcap}，筛选 MAC 地址: {mac_address}")
    filtered_packets = []

    with PcapReader(input_pcap) as pcap_reader:
        for pkt in pcap_reader:
            if pkt.haslayer("Ether") and (pkt.src == mac_address or pkt.dst == mac_address):
                filtered_packets.append(pkt)

    print(f"筛选完成，找到 {len(filtered_packets)} 个数据包")
    return filtered_packets


def process_pcap_files(input_folder, output_folder, device_mac_map):
    """处理所有pcap文件，按设备MAC地址拆分流量"""
    os.makedirs(output_folder, exist_ok=True)

    pcap_files = glob.glob(os.path.join(input_folder, "*.pcap"))
    print(f"在 {input_folder} 目录下找到 {len(pcap_files)} 个 pcap 文件")

    for pcap_file in pcap_files:
        date_str = os.path.basename(pcap_file).split(".")[0]  # 提取日期部分
        print(f"\n正在处理 {pcap_file} (日期: {date_str})")

        for device_name, mac_address in device_mac_map.items():
            device_folder = os.path.join(output_folder, device_name)
            os.makedirs(device_folder, exist_ok=True)

            packets = extract_device_packets(pcap_file, mac_address)

            if packets:  # 只有当有流量时才写入
                output_pcap = os.path.join(device_folder, f"{device_name}_{date_str}.pcap")
                wrpcap(output_pcap, packets)
                print(f"[{device_name}] {date_str}: 流量已保存 ({len(packets)} 包) -> {output_pcap}")
            else:
                print(f"[{device_name}] {date_str}: 无流量，跳过")


def main():
    input_folder = "/home/hyj/deviceIdentification/dataset/UNW2016/originalTraffic"  # 输入pcap文件夹路径
    output_folder = "/home/hyj/deviceIdentification/dataset/UNW2016/1_input"  # 输出文件夹路径

    device_mac_map = {
        "Smart Things": "d0:52:a8:00:67:5e",
        "Amazon Echo": "44:65:0d:56:cc:d3",
        "DeviceC": "AA:BB:CC:DD:EE:03"
    }

    print("\n===== 开始处理 pcap 文件 =====")
    process_pcap_files(input_folder, output_folder, device_mac_map)
    print("\n===== 处理完成 =====")


if __name__ == "__main__":
    main()
