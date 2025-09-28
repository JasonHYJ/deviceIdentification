# -*- coding: utf-8 -*-

"""
progress1.2：优化后的代码，使用PcapReader逐个数据包读取，而不是一次性加载整个文件。这种方法对内存更友好，特别适合处理大型 .pcap 文件。
读取指定目录下的 .pcap 文件，并将每个 .pcap 文件中的流量按双向流分类，并基于会话的时间跨度进行筛选，然后将筛选后的数据包保存到一个新的目录中。
该文件依赖于to_session_dict.py 中的 to_session_dict 函数

1. 逐包读取 .pcap 文件
    使用 PcapReader 按数据包逐个读取，避免一次性将整个文件加载到内存中。
    记录第一个和最后一个数据包的时间，用于计算文件的时间跨度。
2. 双向流会话分类
    按五元组（源IP、源端口、目的IP、目的端口、协议）对流量进行分类。
    将双向流量归类为同一会话，并存储每个会话的所有数据包。
3. 会话时间筛选
    计算每个会话的时间跨度。
    基于设定的阈值（默认为原始流量时间跨度的 1/2）筛选出符合条件的会话。
4. 结果保存
    将符合时间跨度条件的会话保存为独立的 .pcap 文件。
    文件名格式为 {src_ip}_{src_port}_{dst_ip}_{dst_port}_{proto}.pcap。
5. 批量处理与目录管理
    支持批量处理指定目录下的所有 .pcap 文件。
    按设备和会话分别创建输出目录，保留原始目录结构。
"""

import os
from scapy.all import PcapReader, wrpcap
from collections import defaultdict


def to_session_dict(pcap_file, output_dir, num=1 / 2):  # num用于定义会话时间跨度相对于原始文件的阈值，默认为原始时间跨度的1/2
    # 使用PcapReader逐包读取
    sessions = defaultdict(list)
    packet_count = 0
    first_packet_time = None
    last_packet_time = None

    # 遍历每个数据包，按五元组分类
    with PcapReader(pcap_file) as pcap_reader:
        for packet in pcap_reader:
            packet_count += 1
            if packet_count == 1:
                first_packet_time = packet.time
            last_packet_time = packet.time

            if packet.haslayer('IP') and (packet.haslayer('TCP') or packet.haslayer('UDP')):
                ip_layer = packet['IP']
                proto_layer = packet['TCP'] if packet.haslayer('TCP') else packet['UDP']

                # 获取会话，即双向流的五元组 (源IP, 源端口, 目的IP, 目的端口, 协议)
                flow_tuple = tuple(
                    sorted([(ip_layer.src, proto_layer.sport, ip_layer.dst, proto_layer.dport, ip_layer.proto),
                            (ip_layer.dst, proto_layer.dport, ip_layer.src, proto_layer.sport, ip_layer.proto)]))
                sessions[flow_tuple].append(packet)

    if not sessions:
        print(f"No valid packets found in {pcap_file}. Skipping...")
        return

    original_duration = last_packet_time - first_packet_time
    duration_threshold = original_duration * num  # 定义时间跨度限制条件，将阈值设备原始文件时长的一定比例（1/2）

    os.makedirs(output_dir, exist_ok=True)

    # 将每个会话写入单独的PCAP文件，满足时间跨度条件的会话
    for flow_tuple, flow_packets in sessions.items():
        flow_start_time = flow_packets[0].time
        flow_end_time = flow_packets[-1].time
        flow_duration = flow_end_time - flow_start_time

        if flow_duration >= duration_threshold:
            src_ip, src_port, dst_ip, dst_port, proto = flow_tuple[0]  # 取其中一个方向
            filename = f'{src_ip}_{src_port}_{dst_ip}_{dst_port}_{proto}.pcap'
            filepath = os.path.join(output_dir, filename)
            wrpcap(filepath, flow_packets)

    print(f"满足时长的会话提取完成，结果保存在目录: {output_dir}")


# 定义主函数
def main():
    input_dir = r'artifact/data/samples/pcaps'
    out_dir = r'artifact/outputs/period/2_output'

    for root, dirs, files, in os.walk(input_dir):
        for file in files:
            if file.endswith(".pcap"):
                pcap_file = os.path.join(root, file)  # 获取文件路径
                filename = os.path.splitext(file)[0]  # 获取文件名，不包括扩展名

                out_device_dir = os.path.join(out_dir, os.path.relpath(root, input_dir))  # 该设备文件输出的保存目录
                out_file_dir = os.path.join(out_device_dir, filename)  # 当前文件划分的会话文件的保存目录

                if not os.path.exists(out_file_dir):
                    os.makedirs(out_file_dir)  # 如果文件输出目录不存在，则创建该目录

                to_session_dict(pcap_file, out_file_dir, 1 / 2)  # 处理PCAP文件，提取满足时长条件的会话并保存结果


# 检查是否作为主程序运行
if __name__ == "__main__":
    main()
