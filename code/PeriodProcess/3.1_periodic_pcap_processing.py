# -*- coding: utf-8 -*-
"""
progress3.1：将代码进行优化，遍历所有目录，当找到pcap文件之后，进行处理。
它的主要功能包括检查 .pcap 文件的周期信息，删除不符合条件的文件，并将符合条件的文件按周期信息进行拆分并存储。

1. 二进制时间序列转换
    通过 convert_pcap_to_binary_timeseries 将 .pcap 文件转化为二进制时间序列，表示每秒是否有数据包。
2. 周期提取与分析
    使用 identify_candidate_periods 提取可能的周期。
    通过 calculate_autocorrelation 计算候选周期的自相关性，分析其有效性。
    调用 extract_flow_periods 返回可能的周期性模式。
3. 周期筛选与文件拆分
    使用 find_closest_pair 找到最稳定的周期。
    根据最佳周期，调用 split_pcap_by_period 按周期拆分 .pcap 文件并保存。
4. 结果保存
    在每个 .pcap 文件对应的目录中创建 record.txt 文件，记录候选周期和最佳周期信息。
5. 自动化批量处理
    遍历指定路径下的所有 .pcap 文件。
    删除没有周期性模式的文件。
    将符合条件的文件拆分并保存到对应目录。
6. 统计与输出
    打印每个会话的处理结果。
    统计总处理会话数和总拆分的文件数。
"""

import os
import numpy as np
from scapy.all import *
from scapy.all import rdpcap
from scipy.fft import fft
import math
# from tool.cloest_pair_period import find_closest_pair
# from tool.split_flow_by_period import split_pcap


# 将 .pcap 文件中的数据包转换为二进制时间序列。如果某秒内有数据包，二进制序列中对应的位置为 1。如果某秒内没有数据包，二进制序列中对应的位置为 0。
def pcap_to_binary_timeseries(pcap_file):
    packets = rdpcap(pcap_file)
    start_time = packets[0].time
    end_time = packets[-1].time
    duration = int(end_time - start_time) + 1
    binary_timeseries = []

    current_time = start_time
    index = 0
    for packet in packets:
        # 如果当前秒内没有数据包（即 packet.time 比 current_time + 1 更晚），则使用 while 循环为每个缺失的秒数填充 0，直到到达当前数据包的时间。
        while packet.time >= current_time + 1:
            # If no packet in this second, append 0
            binary_timeseries.append(0)
            current_time += 1
        # 当 packet.time 等于 current_time 时，while 循环结束，当前秒内有数据包，因此将 1 添加到 binary_timeseries 中，表示这一秒内有数据包。
        binary_timeseries.append(1)
        current_time += 1

    # Fill the remaining seconds with 0
    while current_time <= end_time:
        binary_timeseries.append(0)
        current_time += 1

    return binary_timeseries


# 利用fft分析输入的时间序列（二进制序列），提取周期信号。从输入序列中找到可能的周期并返回这些周期的候选列表。
def _f_period(x):
    y = fft(x)
    amplitudes = abs(y)  # 振幅计算，振幅表示信号在对应频率上的强度。
    t_amplitude = amplitudes.max() * 0.1  # 设定阈值：取振幅的最大值，并乘以 0.1，得到一个阈值 t_amplitude。
    candidate_period = []
    """
    遍历振幅数组，从第二个元素到倒数第二个元素，
    峰值检测：对每个频率 i：
    振幅需要大于等于 t_amplitude（即超过设定的阈值）。
    同时，这个频率的振幅应该比其相邻的频率振幅更大（形成一个局部峰值）。
    如果满足以上条件，该频率 i 被认为是候选周期，添加到 candidate_period 列表中。
    """
    for i in range(1, len(amplitudes) - 1):
        if amplitudes[i] >= t_amplitude and amplitudes[i] > amplitudes[i - 1] and amplitudes[i] > amplitudes[i + 1]:
            candidate_period.append(i)
    """
    候选周期 i 被转换为对应的时间周期 t,为了增加候选周期的鲁棒性，t 被扩展到一个范围[90%-110%]，参数可调整
    在这个范围内的整数，都认为是候选周期，添加到 candidate_period_t 列表中。
    最终，将 candidate_period_t 列表去重，确保每个候选周期只出现一次。
    """
    candidate_period_t = []
    for i in range(0, len(candidate_period)):
        t = len(x) / candidate_period[i]
        t_upper_bound = int((1.1 * t))
        t_lower_bound = math.ceil(0.9 * t)
        for j in range(t_lower_bound, t_upper_bound):
            candidate_period_t.append(j)
        candidate_period_t = list(set(candidate_period_t))
    return candidate_period_t


# 计算和评估在给定周期 i 的情况下，时间序列 x 的自相关性。它计算自相关函数值，并通过这些值来判断周期的有效性。
# x：时间序列数据，二进制表示的数组。
# i：待评估的周期长度。
def _r_rn(x, i):
    n = len(x)
    # print(n)
    if i >= (n - 1) or i < 1:
        return []
    """
    计算时间序列 x 在周期 i 下的自相关值。
    x[i:] 表示从索引 i 开始到序列末尾的部分。
    x[:n - i] 表示从序列开始到索引 n−i 的部分。
    np.dot 计算这两个部分的内积（点积），即它们的自相关值。内积（点积）：计算两个向量（或时间序列部分）之间的相似性。
    r_yy_i_l1：计算周期 i−1 下的自相关值。r_yy_i_u1：计算周期 i+1 下的自相关值。这些计算用于比较周期 i 和其相邻周期 i−1 和 i+1 的自相关值。
    """
    r_yy_i = np.dot(x[i:], x[:n - i])
    r_yy_i_l1 = np.dot(x[i - 1:], x[:n - i + 1])
    r_yy_i_u1 = np.dot(x[i + 1:], x[:n - i - 1])
    # 有效性检查：判断在周期 i 下的自相关值是否大于其相邻周期的自相关值。
    if r_yy_i <= r_yy_i_l1 or r_yy_i <= r_yy_i_u1:
        return []
    # 相关度和自相关和是衡量时间序列周期性的重要指标。
    # 相关度用于评估时间序列在给定周期下的自相关性。它反映了时间序列在周期 i 下的内积的大小。
    # 自相关和是一个量度，用于综合考虑周期i、周期i−1、和周期i+1 下的自相关值。它反映了时间序列在多个周期下的整体相关性。
    r = i * r_yy_i / n
    r_n = i * (r_yy_i + r_yy_i_l1 + r_yy_i_u1) / n
    return [r, r_n]


def flow_data_process(x):
    result = {}
    candidate_period = _f_period(x)
    for i in candidate_period:
        r_rn_result = _r_rn(x, i)
        if r_rn_result:
            result[i] = r_rn_result

    return result


# flow_to_periods：分析 .pcap 文件中的数据流，提取并识别可能的周期性模式。
# 脚本的主要流程包括读取 .pcap 文件，将其转换为二进制时间序列，然后使用傅里叶变换和相关性分析来识别潜在的周期性。
def flow_to_periods(input_pcap_file):
    binary_timeseries = pcap_to_binary_timeseries(input_pcap_file)
    return flow_data_process(binary_timeseries)


# 在给定的字典中找到一个周期，这个对的自相关性最接近一个理想的稳定值。该函数根据周期的自相关值（ri 和 rni）来评估周期的稳定性，并找到与稳定条件最接近的周期对。
# 首选 ri >= 1 的周期对,如果没有找到符合 ri >= 1 的周期对，则放宽条件，尝试找到最接近稳定条件的周期对。
# 最好的差值：最接近稳定条件的周期对的 diff 应尽可能小，理想情况下 diff 应为 0。这表明周期对的 ri 和 rni 值非常接近理想值 1。
def find_closest_pair(dictionary):
    best_diff = float('inf')  # 最小差值
    closest_pair = None

    # 首先在 ri >= 1 的候选周期中寻找最接近稳定条件的周期
    for k, v in dictionary.items():
        ri, rni = v

        # 排除不稳定周期
        if ri < 1 and ri < 0.1 * rni:
            continue

        # 如果 ri >= 1，则计算与稳定条件的差值,即 ri 和 rni 距离理想稳定值 1 的总和
        if ri >= 1:
            diff = abs(ri - 1) + abs(rni - 1)
            if diff < best_diff:
                best_diff = diff
                closest_pair = (k, v)

    # 如果没有找到合适的周期，再放宽条件在 ri < 1 中寻找
    if closest_pair is None:
        for k, v in dictionary.items():
            ri, rni = v

            # 再次排除不稳定周期
            if ri < 1 and ri < 0.1 * rni:
                continue

            # 计算与稳定条件的差值
            diff = abs(ri - 1) + abs(rni - 1)
            if diff < best_diff:
                best_diff = diff
                closest_pair = (k, v)

    return closest_pair


def split_pcap(input_file, output_folder, time_interval_seconds):
    packets = rdpcap(input_file)  # 读取输入的 pcap 文件
    start_time = packets[0].time  # 获取第一个数据包的时间戳
    current_interval = start_time
    current_output = None
    file_count = 0  # 计数器：当前会话生成的文件数量

    for packet in packets:
        if packet.time >= current_interval:
            # 创建新的输出 pcap 文件
            if current_output:
                current_output.close()
            output_filename = f"{output_folder}/output_{int(current_interval)}.pcap"
            current_output = PcapWriter(output_filename, append=True)
            file_count += 1  # 更新文件计数器

            current_interval += time_interval_seconds

        # 写数据包到当前输出文件
        current_output.write(packet)

    if current_output:
        current_output.close()

    return file_count


def process_pcap_files(path):
    total_sessions = 0  # 总共处理的会话数量
    total_files_split = 0  # 总共划分的文件数量
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pcap"):
                filename = os.path.join(root, file)
                print("当前正在处理会话文件: ", filename)
                # 计算当前的会话文件是否具有候选周期
                period = flow_to_periods(filename)
                print("提取当前文件的所有周期信息: ", period)

                if not period:
                    try:
                        os.remove(filename)
                        print("当前文件 ", filename, ' 没有周期，文件删除成功:')
                    except OSError as e:
                        print("文件删除失败:", e)
                # 如果有候选周期，为该会话文件创建一个目录
                else:
                    folder_path = os.path.splitext(filename)[0] # 用于将文件名分割成两部分：文件名和扩展名
                    print('当前周期会话的目录是： ', folder_path)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    # 从所有的候选周期中找到最接近的周期
                    result = find_closest_pair(period)
                    if result is None:
                        try:
                            os.remove(filename)
                            print("当前文件 ", filename, ' 没有最接近的周期，文件删除成功。')
                        except OSError as e:
                            print("文件删除失败:", e)
                    else:
                        # 如果有最佳周期，则创建一个record.txt保存周期情况，其中有候选周期的信息，也有选择的最佳周期的信息
                        txt_file_path = os.path.join(folder_path, "record.txt")
                        print('已为当前会话创建周期的记录文件record.txt')
                        with open(txt_file_path, "w") as txt_file:
                            txt_file.write("候选周期:" + str(period) + "\n" + "选择周期:" + str(result))

                        files_split = split_pcap(filename, folder_path, result[0])
                        print('当前会话文件划分出 ', files_split, ' 个周期段')
                        total_files_split += files_split  # 更新总文件计数器

                        # 删除源文件
                        try:
                            os.remove(filename)
                            print(f"源文件 {filename} 删除成功。")
                        except OSError as e:
                            print(f"源文件 {filename} 删除失败: {e}")

                total_sessions += 1  # 更新会话计数器
            print('******\n')

    print("总共处理的会话文件数量:", total_sessions)
    print("总共划分的文件数量:", total_files_split)


def main():
    path = r'/home/hyj/deviceIdentification/dataset/LabData/3_selectDir'
    process_pcap_files(path)


if __name__ == "__main__":
    main()
