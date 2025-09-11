# -*— coding: utf-8 -*-

"""
根据合并后的字典中的每个会话对应的关键数据包统计情况，
从已经提取的特征的目录9_feature中的每个会话文件夹中随机选择一个样本，验证其中是否包含符合关键数据包分布的特征数据。
如果数据包大小方向一样的数据包完全匹配上，则把对应的数据包提出来，单独保存到一个csv文件中，作为该会话的签名数据。其中只包含关键数据包的特征信息
如果样本完全匹配关键数据包，则提取这些数据包的特征信息并保存为新的 CSV 文件，作为该会话的签名数据。
有的会话关键数据包可能在随机挑选的测试样本中找不到，这就导致有的会话csv文件匹配失败

1. 加载关键数据包分布信息
    从合并后的关键数据包 CSV 文件中读取设备、会话和关键数据包分布信息，存储为字典格式，便于查找。
2. 样本验证
    遍历每个会话中的样本 CSV 文件。
    检查样本数据包是否完全符合关键数据包的分布要求。
3. 特征数据提取与保存
    对符合关键数据包分布的样本提取其特征向量。
    按设备和会话名创建目录，将结果保存为新的 CSV 文件。
4. 批量处理
    遍历设备和会话文件夹，对每个会话随机选择一个样本进行验证和处理。
    记录成功匹配的会话数量。
5. 输出统计
    打印设备文件夹、会话文件夹总数，以及成功匹配的会话数量。
"""

import os
import csv
import random
import ast


# 读取关键数据包CSV文件，返回一个字典以便快速查找
def read_key_packet_csv(key_packet_csv_path):
    key_packet_info = {}
    print(f"正在读取关键数据包文件: {key_packet_csv_path}")
    with open(key_packet_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_name = row['device_name']
            session_name = row['session_name'].split('___')[0]  # 去掉___及后面的数字
            packet_distribution = ast.literal_eval(row['packet_distribution'])  # 将字符串转换为字典
            key_packet_info[(device_name, session_name)] = packet_distribution
    print("关键数据包信息读取完成。")
    print('***********')
    print()

    return key_packet_info


# 验证样本是否包含关键数据包的分布
def validate_sample(sample_path, key_packets):
    # print(f"正在验证样本文件: {sample_path}")
    sample_packets = {}

    with open(sample_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # 将 frame.len 和 direction 组合为 key
            packet_key = f"{row['frame.len']}_{row['direction']}"
            sample_packets[packet_key] = sample_packets.get(packet_key, 0) + 1  # 统计相同 key 的数量

    # 检查样本中的数据包分布是否与关键数据包分布一致
    for key, count in key_packets.items():
        if sample_packets.get(key, 0) != count:
            # print(f"样本验证失败：缺少关键数据包 {key} 或数量不匹配")
            return False  # 如果有不匹配的 key，返回 False

    # print("样本验证通过。")
    return True  # 全部匹配，返回 True


# 对样本进行排序并匹配关键数据包，然后保存匹配的特征向量到输出文件夹
def process_and_save_sample(sample_path, key_packets, output_folder, device_folder, session_folder):
    print(f"正在处理样本文件: {sample_path}")
    matched_packets = []

    # 读取样本并排序
    packets = []
    with open(sample_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['frame.time_epoch'] = float(row['frame.time_epoch'])
            packets.append(row)
    packets.sort(key=lambda x: x['frame.time_epoch'])  # 按时间戳排序

    # 匹配关键数据包
    key_packets_copy = key_packets.copy()  # 深拷贝一份关键数据包分布
    for packet in packets:
        packet_key = f"{packet['frame.len']}_{packet['direction']}"
        if packet_key in key_packets_copy and key_packets_copy[packet_key] > 0:
            matched_packets.append(packet)  # 记录匹配的数据包
            key_packets_copy[packet_key] -= 1  # 更新匹配的数量

            # 当所有关键数据包都匹配完成时，停止匹配
            if all(count == 0 for count in key_packets_copy.values()):
                print("成功匹配所有关键数据包。")
                break

    # 如果匹配完成，则将匹配到的特征向量保存到新的 CSV 文件中
    if all(count == 0 for count in key_packets_copy.values()):
        # 确保输出文件夹存在
        output_device_folder = os.path.join(output_folder, device_folder)
        output_session_folder = os.path.join(output_device_folder, f"{session_folder}.csv")
        os.makedirs(output_device_folder, exist_ok=True)

        # 写入新的CSV文件
        fieldnames = ['frame.time_epoch', 'frame.len', 'direction', 'time_interval', 'protocol_type', 'payload',
                      'label']
        with open(output_session_folder, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matched_packets)

        print(f"匹配的数据包已保存到 {output_session_folder}")
        print()
        return True
    else:
        print(f"无法匹配会话 {session_folder} 中的所有关键数据包")
        return False  # 返回未成功匹配的标志


# 主处理函数，遍历设备和会话文件夹，选择样本并处理
def process_samples(root_folder, key_packet_csv_path, output_folder):
    key_packet_info = read_key_packet_csv(key_packet_csv_path)

    total_device_folders = 0
    total_session_folders = 0
    successful_sessions = 0

    for device_folder in os.listdir(root_folder):
        device_path = os.path.join(root_folder, device_folder)
        if not os.path.isdir(device_path):
            continue

        total_device_folders += 1
        print()
        print(f"正在处理设备文件夹: {device_folder}")
        subfolder = os.path.join(device_path, os.listdir(device_path)[0])  # 只获取子文件夹
        for session_folder in os.listdir(subfolder):
            session_path = os.path.join(subfolder, session_folder)
            if not os.path.isdir(session_path):
                continue

            total_session_folders += 1
            # 在关键数据包 CSV 文件中找到与设备和会话名匹配的行
            if (device_folder, session_folder) not in key_packet_info:
                print(f"跳过会话文件夹 {session_folder}，因为没有找到对应的关键数据包信息")
                continue
            key_packets = key_packet_info[(device_folder, session_folder)]

            # 获取会话文件夹中的所有CSV文件
            csv_files = [f for f in os.listdir(session_path) if f.endswith('.csv')]
            if not csv_files:
                print(f"会话 {session_folder} 中没有 CSV 文件")
                continue

            # 遍历所有样本文件进行验证
            for sample_file in csv_files:
                sample_path = os.path.join(session_path, sample_file)
                if validate_sample(sample_path, key_packets):
                    print(f"会话 {session_folder} 中找到有效样本: {sample_file}")
                    if process_and_save_sample(sample_path, key_packets, output_folder, device_folder, session_folder):
                        successful_sessions += 1  # 成功匹配会话数量增加
                    break  # 找到匹配的样本后跳出当前会话的处理
            else:
                print(f"警告: 会话 {session_folder} 中没有找到匹配的样本，跳过该会话\n")

    print(f"共处理了 {total_device_folders} 个设备文件夹，{total_session_folders} 个会话文件夹。")
    print(f"成功匹配的会话数量: {successful_sessions}")


# 主函数
def main():
    root_folder = '/home/hyj/deviceIdentification/dataset/LabData/9_feature'  # 替换为实际的总输入文件夹路径
    key_packet_csv_path = '/home/hyj/deviceIdentification/dataset/LabData/14_keyPacketMerge/14_keyPacketMerge_merged_results.csv'  # 替换为实际的关键数据包CSV文件路径
    output_folder = '/home/hyj/deviceIdentification/dataset/LabData/15_keyPacketSignature'  # 替换为实际的输出目录

    # key_packet_csv_path = '/home/hyj/deviceIdentification/dataset/test1/uk/uk_merged_results.csv'
    # output_folder = '/home/hyj/deviceIdentification/dataset/test/uk'

    print("程序开始执行...")
    process_samples(root_folder, key_packet_csv_path, output_folder)
    print("程序执行完毕。")


if __name__ == '__main__':
    main()
