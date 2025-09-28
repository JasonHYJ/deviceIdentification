# -*- coding: utf-8 -*-

"""
对于selectDir中得到的那一天的流量，复制到新的目录suitableDir之后，判断其中的每个会话是否具有足够的样本数目。
如果具有则保留会话文件夹，如果没有则删除会话文件夹，最终只保留具有足够数目样本的会话文件夹。
实现的功能：
1、复制文件：将源文件夹 src_folder 中的所有文件和子目录复制到目标文件夹 dst_folder。
2、过滤操作：检查目标文件夹中每个会话文件夹（包含 .pcap 文件的文件夹），如果 .pcap 文件数量少于 15 个，则删除该会话文件夹。
3、输出信息：在操作过程中打印每个文件的复制路径和被删除的会话文件夹路径。

1. 文件和目录复制
    将源目录下的所有文件和子目录完整复制到目标目录中。
    记录每个复制文件的源路径和目标路径。
2. 会话过滤与清理
    遍历目标目录，检查每个会话文件夹中的 .pcap 文件数量。
    如果某个会话文件夹中的 .pcap 文件少于 15 个，则删除该会话文件夹。
    打印被删除的会话文件夹路径。
3. 主函数执行流程
    设置源目录和目标目录路径。
    确保目标目录存在。
    执行复制操作。
    对目标目录中的会话文件夹进行筛选和清理。
"""

import os
import shutil


def copy_all_files(src_folder, dst_folder):
    # 复制源文件夹下的所有文件及目录到目标文件夹
    for root, dirs, files in os.walk(src_folder):
        # 计算相对路径
        rel_path = os.path.relpath(root, src_folder)
        dst_path = os.path.join(dst_folder, rel_path)

        # 创建目标路径中的文件夹
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        # 复制文件
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_path, file)
            shutil.copy2(src_file, dst_file)
            print(f"Copied: {src_file} -> {dst_file}")


def filter_and_clean(dst_folder):
    # 在目标文件夹下进行过滤操作
    for root, dirs, files in os.walk(dst_folder):
        # 只处理包含 .pcap 文件的会话文件夹
        pcap_files = [f for f in files if f.endswith('.pcap')]

        if pcap_files:
            if len(pcap_files) < 15:
                # 如果 .pcap 文件数量小于15，则删除会话文件夹
                shutil.rmtree(root)
                print(f"Deleted: {root}")


def main():
    src_folder = 'artifact/outputs/period/3_selectDir'  # 源文件夹路径
    dst_folder = 'artifact/outputs/preproc/4_suitableDir'  # 目标文件夹路径

    # 确保目标文件夹存在
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    # 先复制所有文件到新路径
    copy_all_files(src_folder, dst_folder)

    # 然后在新路径下进行过滤操作
    filter_and_clean(dst_folder)


# 运行主函数
if __name__ == "__main__":
    main()
