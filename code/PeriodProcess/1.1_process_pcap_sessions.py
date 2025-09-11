# -*- coding: utf-8 -*-


"""
progress1.1：优化后的代码，使用rdpcap将整个 .pcap 文件加载到内存中进行处理
读取指定目录下的 .pcap 文件，并将每个 .pcap 文件中的流量按双向流分类，并基于会话的时间跨度进行筛选，然后将筛选后的数据包保存到一个新的目录中。
该文件依赖于to_session_dict.py 中的 to_session_dict 函数

1. 读取与解析 .pcap 文件
    使用 scapy 的 rdpcap 函数加载 .pcap 文件到内存。
    计算原始流量的时间跨度。
2. 双向流会话分类
    按五元组（源IP、源端口、目的IP、目的端口、协议）对流量进行分类。
    将双向流量归类为同一会话。
3. 会话时间筛选
    计算每个会话的时间跨度。
    根据设定的阈值（默认为原始流量时间跨度的 1/2）筛选出符合条件的会话。
4. 结果保存
    将符合时间跨度条件的会话保存为独立的 .pcap 文件。
    文件名格式为 {src_ip}_{src_port}_{dst_ip}_{dst_port}_{proto}.pcap。
5. 目录结构与批量处理
    保留设备和会话文件夹的原始目录结构。
    批量处理指定目录下的所有 .pcap 文件，并将结果保存到目标目录。
"""


import os
from scapy.all import rdpcap, wrpcap
from collections import defaultdict


def to_session_dict(pcap_file, output_dir, num=1 / 2):  # num用于定义会话时间跨度相对于原始文件的阈值，默认为原始时间跨度的1/2
    packets = rdpcap(pcap_file)

    # 获取原始PCAP的时间跨度
    original_start_time = packets[0].time
    original_end_time = packets[-1].time
    original_duration = original_end_time - original_start_time

    # 存储分类后的会话
    sessions = defaultdict(list)

    # 遍历每个数据包，按五元组分类
    for packet in packets:
        if packet.haslayer('IP') and (packet.haslayer('TCP') or packet.haslayer('UDP')):
            ip_layer = packet['IP']
            if packet.haslayer('TCP'):
                proto_layer = packet['TCP']
            else:
                proto_layer = packet['UDP']

            # 获取会话，即双向流的五元组 (源IP, 源端口, 目的IP, 目的端口, 协议)
            flow_tuple = tuple(
                sorted([(ip_layer.src, proto_layer.sport, ip_layer.dst, proto_layer.dport, ip_layer.proto),
                        (ip_layer.dst, proto_layer.dport, ip_layer.src, proto_layer.sport, ip_layer.proto)]))
            sessions[flow_tuple].append(packet)

    if not sessions:
        print(f"No valid packets found in {pcap_file}. Skipping...")
        return

    os.makedirs(output_dir, exist_ok=True)  # 创建输出目录，如果目录已经存在，则忽略错误。

    # 定义时间跨度限制条件，将阈值设备原始文件时长的一定比例（1/2）
    duration_threshold = original_duration * num

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
    input_dir = r'/home/hyj/deviceIdentification/dataset/MonIoTr/1_input/uk'
    out_dir = r'/home/hyj/deviceIdentification/dataset/MonIoTr/2_output/uk'

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
