# -*- coding: utf-8 -*-

"""
progress2.1：优化后的代码，使用os.walk找到设备文件夹，然后对每个设备的所有子文件夹进行pcap文件数目判断，选择数目最多的一个，保存到新的目录下

1. 查找包含最多 .pcap 文件的子文件夹
    get_subfolder_with_max_pcap：
        遍历每个设备文件夹的所有子文件夹。
        统计每个子文件夹中 .pcap 文件的数量。
        返回包含最多 .pcap 文件的子文件夹路径。
2. 复制文件夹及其内容
    copy_selected_subfolder：
        将选定的子文件夹及其内容复制到目标路径。
        如果目标路径已存在对应文件夹，则先删除，确保数据最新。
3. 批量处理设备文件夹
    遍历顶层目录，查找所有设备文件夹。
    对每个设备文件夹执行上述步骤，筛选并复制子文件夹到目标路径。
4. 进度输出
    打印每个选定子文件夹的路径和复制操作的结果。
"""
import os
import shutil


# 找到当前设备包含最多 pcap 文件的子文件夹，输入设备文件夹路径，return包含最多 pcap 文件的子文件夹路径
def find_subfolder_with_most_pcap(root_folder):
    max_pcap_count = 0
    selected_subfolder = None

    # 遍历设备文件夹中的所有子文件夹
    for root, dirs, files in os.walk(root_folder):
        if root == root_folder:
            continue  # 跳过设备文件夹本身，只遍历其子文件夹
        pcap_count = sum(1 for file in files if file.endswith('.pcap'))
        if pcap_count > max_pcap_count:
            max_pcap_count = pcap_count
            selected_subfolder = root
    return selected_subfolder


# 复制文件夹及其内容到目标路径。
def copy_folder(src, dst):
    # 在目标路径中创建一个新的文件夹，名字与selected_subfolder相同
    final_dst = os.path.join(dst, os.path.basename(src))

    if os.path.exists(final_dst):
        shutil.rmtree(final_dst)  # 如果目标文件夹存在，先删除，确保数据内容最新
    shutil.copytree(src, final_dst)  # 将src目录及下面的所有内容，复制到final_dst下面。


def main():
    input_path = r'artifact/outputs/period/2_output'
    out_path = r'artifact/outputs/period/3_selectDir'
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    for root, dirs, files in os.walk(input_path):
        # 只在顶层目录中查找设备文件夹
        if root == input_path:
            # 对每个设备文件夹执行函数，查找其中包含pcap数目最多的子文件夹
            for device_folder in dirs:
                device_path = os.path.join(root, device_folder)
                selected_subfolder = find_subfolder_with_most_pcap(device_path)
                print("选择的目录是：", selected_subfolder)
                # 将找到的子文件夹及其内容复制到目标路径下。
                if selected_subfolder:
                    destination_folder = os.path.join(out_path, device_folder)
                    print("目标目录是：", destination_folder)
                    copy_folder(selected_subfolder, destination_folder)
                    print(f"Copied {selected_subfolder} to {destination_folder}")
            # 只处理顶层目录下的设备文件夹，所以跳出循环
            break


if __name__ == "__main__":
    main()
