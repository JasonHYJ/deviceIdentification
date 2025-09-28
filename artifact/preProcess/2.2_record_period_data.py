# -*- coding: utf-8 -*-

"""
用来遍历指定目录下的子目录，并读取每个子目录中的 .txt 文件的最后一行内容，然后将这些内容记录到一个指定的记录文件 (period_record.txt) 中。
此代码非必要项，只是为了记录整合一下所有的周期记录
实现的功能：
1、遍历给定目录下的所有子目录及文件，定位所有以 .txt 结尾的文件。
2、读取每个 .txt 文件的最后一行内容。
3、将这些内容按照特定格式记录到 period_record.txt 文件中，同时根据设备名称对记录进行分段。

1. 读取最后一行内容
    read_last_line 函数读取 .txt 文件的最后一行。
    处理空文件时返回空字符串。
2. 写入汇总记录
    write_to_txt_file 函数将内容追加写入 period_record.txt。
3. 遍历与分类记录
    遍历指定目录，查找所有 .txt 文件。
    按设备分类记录周期信息，在设备更换时插入空行分隔。
    将记录格式化为：
        设备名称 设备的 会话名称 周期信息
5. 控制台输出
    打印记录到控制台，便于实时查看和调试。
"""

import os


# 读取指定文件的所有行，并返回文件的最后一行。如果文件为空，则返回空字符串。
def read_last_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if not lines:
            return ""
        return lines[-1].strip()


# 将指定内容追加到指定的 .txt 文件中。
def write_to_txt_file(file_path, content):
    with open(file_path, 'a') as file:
        file.write(content)


def main():
    start_path = r'artifact/outputs/preproc/4_suitableDir'
    period_record = os.path.join(start_path, 'period_record.txt')

    previous_device = None  # 用来跟踪上一个处理的设备

    # 遍历根目录下的所有内容
    for root, dirs, files in os.walk(start_path):
        for file_name in files:
            if file_name.endswith('.txt'):
                # 获取当前 txt 文件所在文件夹路径
                session_folder = os.path.basename(root)

                # 获取 device 文件夹的名称
                device_name = os.path.basename(os.path.dirname(os.path.dirname(root)))

                # 检查是否换了一个设备
                if previous_device and previous_device != device_name:
                    # 如果换了设备，先在文件中空一行
                    write_to_txt_file(period_record, "\n")

                # 更新 previous_device
                previous_device = device_name

                # 构建 txt 文件的完整路径
                txt_path = os.path.join(root, file_name)

                # 读取最后一行
                last_line = read_last_line(txt_path)

                # 准备写入的内容
                content = f"{device_name} 设备的 {session_folder} {last_line}\n"
                print(content.strip())  # 打印到控制台

                # 写入 period_record.txt
                write_to_txt_file(period_record, content)


if __name__ == "__main__":
    main()
