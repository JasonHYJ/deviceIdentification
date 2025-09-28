# -*- coding: utf-8 -*-

"""
遍历文件夹，对每个会话csv文件中的样本进行聚类，从csv文件中提取出所需要的特征，对文件中的所有数据包进行聚类，
并将得到的聚类结果，即数据包的聚类集群，保存成csv文件，保存到另一个目录下。每个文件中都是聚到一起的数据包的集合。

1. 读取与特征选择
    从每个 CSV 文件中提取特征列：frame.len、direction、protocol_type。
    将 protocol_type 列转换为数值型。
2. 数据标准化
    使用 StandardScaler 对特征数据进行标准化处理。
3. 聚类操作
    使用 DBSCAN 聚类算法对数据进行聚类。
    为每个样本分配聚类标签，并将标签添加到原始数据中。
4. 聚类结果保存
    根据聚类标签，将每个聚类的样本保存到单独的 CSV 文件中，噪声样本保存为 noise_samples.csv。
5. 统计与评估
    统计噪声样本比例和聚类数量。
    计算聚类的轮廓系数，评估聚类效果。
6. 目录结构的保留与输出
    保留原始的设备和会话目录结构。
    将聚类结果保存到指定的输出根目录。
"""

import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score


# 定义处理单个 CSV 文件的函数
def process_csv(csv_file, output_root_folder):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)

    # 选择用于聚类的特征，有大小，方向，协议类型
    features = df[['frame.len', 'direction', 'protocol_type']]

    # 将 'protocol_type' 转换为数值型，使用 .loc 避免警告
    features.loc[:, 'protocol_type'] = features['protocol_type'].astype('category').cat.codes

    # 规范化数据
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # 使用 DBSCAN 进行聚类
    dbscan = DBSCAN(eps=0.01, min_samples=5)
    clusters = dbscan.fit_predict(scaled_features)

    # 将聚类结果添加到原数据框中
    df['cluster'] = clusters

    # 获取设备文件夹名称
    device_folder = os.path.basename(os.path.dirname(csv_file))
    # 获取会话文件名（不含扩展名）
    session_name = os.path.splitext(os.path.basename(csv_file))[0]

    # 创建输出目录结构：output_root_folder/设备文件夹/会话文件夹
    output_session_dir = os.path.join(output_root_folder, device_folder, session_name)
    if not os.path.exists(output_session_dir):
        os.makedirs(output_session_dir)

    # 创建一个字典来存储聚类标签及其对应的样本索引
    cluster_dict = {}

    # 遍历所有样本，按聚类标签将样本分组
    for index, row in df.iterrows():
        cluster_label = row['cluster']
        if cluster_label not in cluster_dict:
            cluster_dict[cluster_label] = []
        cluster_dict[cluster_label].append(f"样本{index}")

    # 打印每个聚类标签的样本
    for cluster_label, samples in cluster_dict.items():
        if cluster_label == -1:
            print(f"噪声样本: {samples}")
        else:
            print(f"聚类标签{cluster_label}, num= {len(samples)} : {samples}")

    # 计算噪声数据所占的比例
    num_noise_samples = len(df[df['cluster'] == -1])
    total_samples = len(df)
    noise_ratio = num_noise_samples / total_samples

    # 计算簇的个数
    num_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)  # 不包括噪声簇

    # 打印噪声数据比例和簇的个数
    print(f"噪声数据所占比例: {noise_ratio:.2f}")
    print(f"簇的个数: {num_clusters}")

    # 计算聚类评价指标：轮廓系数
    # 注意：轮廓系数需要每个样本都有一个簇，因此噪声样本需要排除
    if len(set(clusters)) > 1:  # 确保有至少两个簇
        try:
            silhouette_avg = silhouette_score(scaled_features, clusters)
            print(f"轮廓系数: {silhouette_avg:.2f}")
        except ValueError:
            print("无法计算轮廓系数，可能因为簇的数量不足。")
    else:
        print("轮廓系数无法计算，因为簇的数量不足。")

    # 遍历所有聚类标签，将每个聚类的样本保存到单独的 CSV 文件中
    for cluster_label in set(clusters):
        cluster_samples = df[df['cluster'] == cluster_label].copy()

        # 添加一列 'original_index' 来显示样本在原始数据中的行号
        cluster_samples.loc[:, 'original_index'] = cluster_samples.index

        # 将 'original_index' 列移到第一列
        columns = ['original_index'] + [col for col in cluster_samples.columns if col != 'original_index']
        cluster_samples = cluster_samples[columns]

        # 保存聚类样本到新的 CSV 文件
        file_name = f'{output_session_dir}/noise_samples.csv' if cluster_label == -1 else f'{output_session_dir}/cluster_{cluster_label}_samples.csv'
        cluster_samples.to_csv(file_name, index=False)
        print(f"已保存聚类标签 {cluster_label} 的样本到文件 {file_name}")


# 使用 os.walk 遍历总文件夹，处理每个CSV文件
def process_all_csvs_in_directory(root_folder, output_root_folder):
    # os.walk 会递归遍历根目录下的所有文件和子目录
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.csv'):
                csv_file_path = os.path.join(dirpath, filename)
                print(f"处理文件: {csv_file_path}")

                # 对每个CSV文件执行聚类操作，并将结果保存到新的输出目录
                process_csv(csv_file_path, output_root_folder)
                print()


# main 函数，作为脚本的入口
def main():
    # 原始的 CSV 文件根目录
    root_folder = 'artifact/outputs/preproc/10_featureMerge'
    # 输出的根目录
    output_root_folder = 'artifact/outputs/preproc/11_featureCluster'  # 替换为你的目标输出路径

    # output_root_folder = "/home/hyj/deviceIdentification/dataset/test/us"

    # 开始处理所有CSV文件，并将结果保存到新的目录
    process_all_csvs_in_directory(root_folder, output_root_folder)


# 判断是否作为脚本执行
if __name__ == "__main__":
    main()
