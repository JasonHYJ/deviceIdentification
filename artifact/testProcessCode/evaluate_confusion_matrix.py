# -*- coding: utf-8 -*-
import os
import argparse
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # 服务器无显示时避免 plt.show() 报错
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import matplotlib as mpl
mpl.rcParams['font.family'] = 'DejaVu Sans'  # Avoid font warnings on Colab
import warnings
warnings.filterwarnings("ignore", message="findfont")



# 字体可能在服务器上没有，找不到也不致命
try:
    mpl.rcParams['font.family'] = 'Times New Roman'
except Exception:
    pass

def evaluate_confusion_matrix_from_csv(csv_file_path, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    df = pd.read_csv(csv_file_path, index_col=0)
    device_names = df.index.tolist()
    confusion_matrix = df.to_numpy()

    n = confusion_matrix.shape[0]
    total_samples = confusion_matrix.sum()
    total_correct = sum(confusion_matrix[i][i] for i in range(n))

    accuracy = total_correct / total_samples if total_samples else 0.0

    recalls = []
    for i in range(n):
        true_total = confusion_matrix[i].sum()
        recalls.append(confusion_matrix[i][i] / true_total if true_total else 0.0)
    macro_recall = float(np.mean(recalls)) if recalls else 0.0

    precisions = []
    for i in range(n):
        predicted_total = confusion_matrix[:, i].sum()
        precisions.append(confusion_matrix[i][i] / predicted_total if predicted_total else 0.0)
    macro_precision = float(np.mean(precisions)) if precisions else 0.0

    f1_scores = []
    for p, r in zip(precisions, recalls):
        f1_scores.append(2 * (p * r) / (p + r) if (p + r) else 0.0)
    macro_f1 = float(np.mean(f1_scores)) if f1_scores else 0.0

    print(f"Total Accuracy: {accuracy:.4f}")
    print(f"Macro Recall:   {macro_recall:.4f}")
    print(f"Macro Precision:{macro_precision:.4f}")
    print(f"Macro F1:       {macro_f1:.4f}\n")
    for i, name in enumerate(device_names):
        print(f"{name} - Recall: {recalls[i]:.4f}, Precision: {precisions[i]:.4f}, F1: {f1_scores[i]:.4f}")

    plt.figure(figsize=(10, 8))
    class_names = device_names + ["Unknown"]
    sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=device_names,
                linecolor='gray', cbar_kws={'label': 'Sample Count'},
                annot_kws={"size": 10})
    plt.xticks(fontsize=12, color='black', rotation=45, ha='right')
    plt.yticks(fontsize=12, color='black')
    plt.title('Confusion Matrix', fontsize=18)
    plt.xlabel('Identification result', fontsize=14)
    plt.ylabel('True Devices', fontsize=14)
    plt.tight_layout()
    plt.savefig(out_path)  # 后缀决定格式
    # 不再 plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i",
                        default="artifact/data/samples/testCsv/uk_confusion_matrix.csv",
                        help="Path to confusion matrix CSV.")
    parser.add_argument("--output", "-o",
                        default="artifact/outputs/eval/confusion_matrix.pdf",
                        help="Path to save the plotted confusion matrix.")
    args = parser.parse_args()

    evaluate_confusion_matrix_from_csv(args.input, args.output)

if __name__ == "__main__":
    main()
