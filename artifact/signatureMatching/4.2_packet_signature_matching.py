# -*— coding: utf-8 -*-

"""
利用构建的签名库，对测试流量实现数据包级别的匹配识别。
签名库包含多台设备，每台设备包含多个会话签名，对于每一条签名，各自独立匹配，当某设备的所有会话签名匹配完毕之后，给出报告。
对于测试样本，按照数据包逐一匹配，以签名[342,342,342,350,350,350]为例，测试样本数据包[343,342,342,342,111,350,350,350,120]为例，具体如下：
1、将每个数据包与签名中的关键数据包进行匹配，当与某个关键数据包匹配上时，记录当前关键数据包的索引；
2、维持两种签名调整顺序顺序，
    （1）ideal：将当前索引关键数据包作为第一个包，它后面的包继续跟随，它前面的包挪到后面去。
    例如当匹配到342时，是与签名中第一个342匹配到，索引为0，签名更新为[342,342,342,350,350,350]
    （2）actual：将签名索引逆序与测试样本数据包进行匹配，取匹配到的最后一个同大小数据包。
    例如当匹配到342时，是与签名中第三个342匹配上，此时索引为2，签名更新为[342,350,350,350,342,342]

1. 加载签名库：
    从签名文件中加载所有设备的会话签名信息，每条签名包含关键数据包的特征矩阵。
2. 加载测试样本：
    读取测试流量文件，将每个数据包的信息（大小、方向、协议类型等）解析为结构化数据。
3. 匹配过程：
    对测试样本中的数据包逐一与签名库进行匹配：
        Ideal 顺序：匹配到第一个关键数据包后，签名顺序调整为从该数据包开始的顺序。
        Actual 顺序：逆序匹配，优先匹配签名中最后一个出现的重复数据包，并调整签名顺序。
    同时维持 Ideal 和 Actual 签名逻辑，任何一方完全匹配即可认为会话匹配成功。
4. 匹配结果统计：
    判断设备的所有会话是否全部匹配完成，如果匹配成功，认为该设备的测试样本属于签名库中的设备。
5. 保存匹配结果：
    将匹配结果以设备名和匹配状态的形式保存为 CSV 文件，便于后续分析。
"""


import pandas as pd
import json


# 加载签名文件，解析JSON格式的签名字段
def load_signatures(signature_file):
    """
    加载设备签名库中的签名文件。
    - 该函数读取CSV文件，并解析每个设备的签名数据（signature列是JSON格式的字符串）。
    """
    print("加载签名文件...")
    # 使用 pandas 读取 CSV 文件
    signatures = pd.read_csv(signature_file)

    # 解析 signature 列中的 JSON 字符串为 Python 对象
    signatures['signature'] = signatures['signature'].apply(json.loads)
    print(f"成功加载 {len(signatures)} 条签名记录。\n")

    # 返回加载的签名数据
    return signatures


# 加载测试样本文件
def load_test_sample(test_file):
    """
    加载测试样本文件。
    - 该函数读取 CSV 文件并返回数据包内容。
    """
    print("加载测试样本文件...")
    test_sample = pd.read_csv(test_file)
    print(f"成功加载 {len(test_sample)} 条测试样本数据包。\n")
    return test_sample


# 提取协议类型：如果包含'tcp'则返回'tcp'，如果包含'udp'则返回'udp'，否则返回'unknown'
def extract_protocol(protocols):
    """
    提取协议类型。如果协议字符串包含 'tcp' 则返回 'tcp'，包含 'udp' 则返回 'udp'，否则返回 'unknown'。
    """
    if 'tcp' in protocols:
        return 'tcp'
    elif 'udp' in protocols:
        return 'udp'
    return 'unknown'


def match_signatures(test_sample, signatures):
    """
    对测试样本与签名库中的每个设备签名进行匹配。
    - 逐个数据包与每个设备的签名中的关键数据包进行比对。
    - 如果测试样本中的数据包按顺序与签名中的所有关键数据包匹配，则认为该设备匹配成功。
    """
    print("开始匹配测试样本与签名库...")
    device_match_results = {}

    # 提取协议类型
    test_sample['protocol_type'] = test_sample['frame.protocols'].apply(extract_protocol)

    # 按设备分组签名
    grouped_signatures = signatures.groupby('device_name')

    for device_name, device_signatures in grouped_signatures:
        print(f"\n正在处理设备：{device_name}")
        # 初始设备匹配状态为 False，表示没有匹配
        device_match_results[device_name] = False  # 初始匹配状态为 False

        # 动态匹配表，每个会话一个记录
        session_match_status = {}
        for _, row in device_signatures.iterrows():
            session_name = row['session_name']
            session_signatures = row['signature']
            session_match_status[session_name] = {
                'signatures': session_signatures,  # 当前会话的签名列表，计划只在更新逻辑签名时使用
                'current_index': 0,  # 当前匹配的关键数据包索引
                'signatures_ideal': None,  # 当前会话的签名列表的逻辑理想签名
                'current_index_ideal': 0,  # 索引
                'signatures_actual': None,  # 当前会话的签名列表的逻辑实际签名
                'current_index_actual': 0,  # 索引
                'matched': False,  # 是否完全匹配
            }
        # 遍历测试样本逐条匹配
        for _, test_packet in test_sample.iterrows():
            for session_name, session_status in session_match_status.items():
                if session_status['matched']:
                    continue  # 如果会话已匹配完成，跳过
                # 在第一次有数据包匹配到签名中时：维护两个逻辑签名：ideal&actual, 根据代码逻辑，必定创建；并且必定同时创建
                if session_status['current_index'] == 0: # 在第一次匹配到数据包时进行签名库的逻辑更新,该代码块仅执行一次。
                    # 一：维护ideal签名；
                    # 在第一次有数据包匹配到签名中时：1）匹配到current_index以外的其他关键数据包 2）刚好匹配到第一个关键数据包
                    if any(
                            (test_packet['frame.len'] == signature['frame.len'] and
                             test_packet['direction'] == signature['direction'] and
                             test_packet['protocol_type'] == signature['protocol_type'])
                            for idx, signature in enumerate(session_status['signatures'])
                            if (match_index_ideal := idx) is not None  # 记录匹配的索引
                    ):
                        session_status['signatures_ideal'] = session_status['signatures'][match_index_ideal:] + \
                                                             session_status['signatures'][:match_index_ideal]

                        session_status['current_index_ideal'] += 1
                        if session_status['current_index_ideal'] == len(session_status['signatures']):
                            session_status['matched'] = True
                            print(f"会话 {session_name} 匹配完成！->ideal")

                    # 二：维护actual签名：
                    # 反向遍历签名列表，优先匹配最后一个重复的包
                    match_index_actual = None
                    for idx, signature in reversed(list(enumerate(session_status['signatures']))):
                        if (test_packet['frame.len'] == signature['frame.len'] and
                                test_packet['direction'] == signature['direction'] and
                                test_packet['protocol_type'] == signature['protocol_type']):
                            match_index_actual = idx
                            break  # 找到匹配的签名后退出循环

                    if match_index_actual is not None:  # 如果找到了匹配的签名
                        # 调整签名顺序：将当前匹配的签名包移到最前
                        session_status['signatures_actual'] = session_status['signatures'][match_index_actual:] + \
                                                              session_status['signatures'][:match_index_actual]
                        # print('更新签名为：'+str(session_status['signatures']))
                        session_status['current_index_actual'] += 1
                        if session_status['current_index_actual'] == len(session_status['signatures']):
                            session_status['matched'] = True
                            print(f"会话 {session_name} 匹配完成！->actual")

                    # 逻辑签名完成更新后废弃原始签名：
                    if session_status['signatures_ideal'] is not None and session_status['signatures_actual'] is not None:
                        session_status['current_index'] = -1
                        print('更新逻辑ideal签名为：'+str(session_status['signatures_ideal']))
                        print('更新逻辑actual签名为：' + str(session_status['signatures_actual']))

                else:  # 已经有关键数据包匹配上(ideal&actual逻辑签名已经完成)
                    # 当前需要匹配的关键数据包
                    current_signature_ideal = session_status['signatures_ideal'][session_status['current_index_ideal']]
                    current_signature_actual = session_status['signatures_actual'][session_status['current_index_actual']]
                    # print('ideal_signature匹配到第'+str(session_status['current_index_ideal'])+'位，下一个等待数据包==>' + str(current_signature_ideal['frame.len']))
                    # print('actual_signature匹配到第'+str(session_status['current_index_actual']) + '位，下一个等待数据包==>' + str(current_signature_actual['frame.len']))
                    # print('----------------------------------------------')

                    # ideal&actual逻辑签名同时进行匹配,任意一个匹配完成就认为会话完成匹配。
                    if (test_packet['frame.len'] == current_signature_ideal['frame.len'] and
                            test_packet['direction'] == current_signature_ideal['direction'] and
                            test_packet['protocol_type'] == current_signature_ideal['protocol_type']):
                        # 匹配成功，更新状态
                        session_status['current_index_ideal'] += 1
                        if session_status['current_index_ideal'] == len(session_status['signatures']):
                            session_status['matched'] = True
                            print(f"会话 {session_name} 匹配完成！->ideal")

                    if (test_packet['frame.len'] == current_signature_actual['frame.len'] and
                            test_packet['direction'] == current_signature_actual['direction'] and
                            test_packet['protocol_type'] == current_signature_actual['protocol_type']):
                        # 匹配成功，更新状态
                        session_status['current_index_actual'] += 1
                        if session_status['current_index_actual'] == len(session_status['signatures']):
                            session_status['matched'] = True
                            print(f"会话 {session_name} 匹配完成！->actual")

        # 检查设备是否所有会话均匹配
        if all(session['matched'] for session in session_match_status.values()):
            device_match_results[device_name] = True
            print(f"设备 {device_name} 的所有会话均匹配完成！")
        else:
            print(f"设备 {device_name} 的匹配未完成。")

            # 重置匹配表，以便下一个测试样本使用
            for session_name in session_match_status:
                session_match_status[session_name]['current_index'] = 0
                session_match_status[session_name]['matched'] = False

    return device_match_results


def save_matching_results(results, output_file):
    """
    将匹配结果保存到CSV文件中。
    """
    # 将结果转换为DataFrame
    result_df = pd.DataFrame(list(results.items()), columns=['device_name', 'match_result'])

    # 保存到CSV文件
    result_df.to_csv(output_file, index=False)
    print(f"匹配结果已保存到 {output_file}\n")


def main():
    """
    主函数：加载文件，执行匹配，打印结果。
    """
    signature_file = "artifact/outputs/merged_signatures/17_signatureMerge/uk/uk_merged_signatures_originalFile.csv"
    test_file = "artifact/data/samples/testCsv/part1.csv"
    output_file = "artifact/outputs/merged_signatures/matching_results.csv"  # 保存匹配结果的文件路径

    # 加载设备签名库和测试样本
    signatures = load_signatures(signature_file)
    test_sample = load_test_sample(test_file)

    # 执行匹配
    results = match_signatures(test_sample, signatures)

    # 打印匹配结果
    print("\n匹配结果：")
    for device_name, is_matched in results.items():
        print(f"设备 {device_name}: {'匹配成功' if is_matched else '匹配失败'}")

    # 保存匹配结果到 CSV 文件
    save_matching_results(results, output_file)


if __name__ == "__main__":
    main()
