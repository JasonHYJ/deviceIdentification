# -*— coding: utf-8 -*-

"""
功能描述：
  该文件遍历 input_folder 下所有子目录的 .csv 文件，对其中的 'payload' 列执行以下操作：
    1) 去除超过 10 个连续的 '0'；
    2) 计算 Nilsimsa 摘要（以 64 位十六进制返回）；
    3) 将该 64 位十六进制哈希转换为 256 位二进制字符串；
    4) 将生成的 256 位字符串替换原有 'payload' 列内容；
  最后将更新后的 CSV 文件保存到 output_folder 下对应的子目录中。
  并统计一共处理了多少个 CSV 文件。

1. 清理 payload 列
    删除 payload 中超过 10 个连续的 0。
2. 生成 Nilsimsa 哈希
    对清理后的 payload 数据生成 64 位十六进制的 Nilsimsa 哈希。
3. 转换为 256 位二进制
    将 Nilsimsa 哈希转换为 256 位二进制字符串。
4. 替换并保存
    用生成的二进制字符串替换原有 payload，保存更新后的 CSV 文件。
5. 保持目录结构
    输出文件保存在与输入目录结构一致的路径中。
6. 统计处理文件
    记录处理的 CSV 文件数量，并在最后打印总数。
"""

import os
import re
import pandas as pd


class Nilsimsa:
    """
   Nilsimsa 类实现了 Nilsimsa 模糊哈希算法，用于判断相似文本/数据块。

   原理概要：
     - 对输入数据的每个字节，结合过去几个字节（形成三元组）进行散列计数（acc）；
     - 通过预定义的 TRAN 查表和运算，将三元组映射到 [0,255] 的一个索引；
     - 每次对该索引的累加器 acc[i] += 1；
     - 最终根据累加器的阈值（与处理的字节数相关）生成 32字节（=256位）的 digest；
     - hexdigest() 则将这 32字节转换为 64 位的十六进制字符串返回。
    """
    def __init__(self):
        # 记录已处理的字节数
        self.count = 0
        # 累加器，用来统计不同三元组被映射到的索引次数
        self.acc = [0] * 256
        # 记录最近的 4 个字节，用于形成三元组
        self.lastch = [-1] * 4
        # 计算出来的 32字节(256位)摘要；若为 None，表示尚未计算或需要重算
        self.digest = None

        # 预定义的查表，用于 tran3() 函数快速映射
        self.TRAN = bytes([
            0x02, 0xD6, 0x9E, 0x6F, 0xF9, 0x1D, 0x04, 0xAB, 0xD0, 0x22, 0x16, 0x1F, 0xD8, 0x73, 0xA1, 0xAC,
            0x3B, 0x70, 0x62, 0x96, 0x1E, 0x6E, 0x8F, 0x39, 0x9D, 0x05, 0x14, 0x4A, 0xA6, 0xBE, 0xAE, 0x0E,
            0xCF, 0xB9, 0x9C, 0x9A, 0xC7, 0x68, 0x13, 0xE1, 0x2D, 0xA4, 0xEB, 0x51, 0x8D, 0x64, 0x6B, 0x50,
            0x23, 0x80, 0x03, 0x41, 0xEC, 0xBB, 0x71, 0xCC, 0x7A, 0x86, 0x7F, 0x98, 0xF2, 0x36, 0x5E, 0xEE,
            0x8E, 0xCE, 0x4F, 0xB8, 0x32, 0xB6, 0x5F, 0x59, 0xDC, 0x1B, 0x31, 0x4C, 0x7B, 0xF0, 0x63, 0x01,
            0x6C, 0xBA, 0x07, 0xE8, 0x12, 0x77, 0x49, 0x3C, 0xDA, 0x46, 0xFE, 0x2F, 0x79, 0x1C, 0x9B, 0x30,
            0xE3, 0x00, 0x06, 0x7E, 0x2E, 0x0F, 0x38, 0x33, 0x21, 0xAD, 0xA5, 0x54, 0xCA, 0xA7, 0x29, 0xFC,
            0x5A, 0x47, 0x69, 0x7D, 0xC5, 0x95, 0xB5, 0xF4, 0x0B, 0x90, 0xA3, 0x81, 0x6D, 0x25, 0x55, 0x35,
            0xF5, 0x75, 0x74, 0x0A, 0x26, 0xBF, 0x19, 0x5C, 0x1A, 0xC6, 0xFF, 0x99, 0x5D, 0x84, 0xAA, 0x66,
            0x3E, 0xAF, 0x78, 0xB3, 0x20, 0x43, 0xC1, 0xED, 0x24, 0xEA, 0xE6, 0x3F, 0x18, 0xF3, 0xA0, 0x42,
            0x57, 0x08, 0x53, 0x60, 0xC3, 0xC0, 0x83, 0x40, 0x82, 0xD7, 0x09, 0xBD, 0x44, 0x2A, 0x67, 0xA8,
            0x93, 0xE0, 0xC2, 0x56, 0x9F, 0xD9, 0xDD, 0x85, 0x15, 0xB4, 0x8A, 0x27, 0x28, 0x92, 0x76, 0xDE,
            0xEF, 0xF8, 0xB2, 0xB7, 0xC9, 0x3D, 0x45, 0x94, 0x4B, 0x11, 0x0D, 0x65, 0xD5, 0x34, 0x8B, 0x91,
            0x0C, 0xFA, 0x87, 0xE9, 0x7C, 0x5B, 0xB1, 0x4D, 0xE5, 0xD4, 0xCB, 0x10, 0xA2, 0x17, 0x89, 0xBC,
            0xDB, 0xB0, 0xE2, 0x97, 0x88, 0x52, 0xF7, 0x48, 0xD3, 0x61, 0x2C, 0x3A, 0x2B, 0xD1, 0x8C, 0xFB,
            0xF1, 0xCD, 0xE4, 0x6A, 0xE7, 0xA9, 0xFD, 0xC4, 0x37, 0xC8, 0xD2, 0xF6, 0xDF, 0x58, 0x72, 0x4E
        ])

    def update(self, data):
        """
        逐字节更新 Nilsimsa 的内部状态：count, acc, lastch。
        data: 任意可迭代字节序列，如 bytes、bytearray 等。
        """
        for ch in data:
            # 保证字节在 [0,255]
            ch = ch & 0xff
            self.count += 1

            # 基于最近的字节组合进行多次 tran3 运算，更新 acc
            if self.lastch[1] > -1:
                self.acc[self.tran3(ch, self.lastch[0], self.lastch[1], 0)] += 1
            if self.lastch[2] > -1:
                self.acc[self.tran3(ch, self.lastch[0], self.lastch[2], 1)] += 1
                self.acc[self.tran3(ch, self.lastch[1], self.lastch[2], 2)] += 1
            if self.lastch[3] > -1:
                self.acc[self.tran3(ch, self.lastch[0], self.lastch[3], 3)] += 1
                self.acc[self.tran3(ch, self.lastch[1], self.lastch[3], 4)] += 1
                self.acc[self.tran3(ch, self.lastch[2], self.lastch[3], 5)] += 1
                self.acc[self.tran3(self.lastch[3], self.lastch[0], ch, 6)] += 1
                self.acc[self.tran3(self.lastch[3], self.lastch[2], ch, 7)] += 1

            # 维护最近 4 个字节
            for i in range(3, 0, -1):
                self.lastch[i] = self.lastch[i - 1]
            self.lastch[0] = ch

        # 每次 update 之后，都需要重新计算 digest
        self.digest = None
        return self

    def tran3(self, a, b, c, n):
        """
        对三个字节 (a, b, c) 和一个偏移 n 做位运算及查表：
          - 结合 TRAN[n]，对 c 做异或
          - 将 (a + n) & 255 的下标和 (b & 0xFF) * (n+n+1) 做 TRAN 查表并异或
          - 再加上 TRAN[i & 0xFF] 并对 255 取模
        返回值为 [0,255] 的一个索引，用来更新 acc。
        """
        i = (c) ^ self.TRAN[n]
        return (
                       (
                               self.TRAN[(a + n) & 255]
                               ^ (self.TRAN[b & 0xff] * (n + n + 1))
                       ) + self.TRAN[i & 0xff]
               ) & 0xff

    def reset(self):
        """
        重置所有内部状态，以便重新计算。
        """
        self.count = 0
        self.acc = [0] * 256
        self.lastch = [-1] * 4
        self.digest = None
        return self

    def compute_digest(self):
        """
        根据 acc 统计信息和处理过的字节数 count 来计算最终的 32字节(256位)摘要。
        超过阈值的 acc[i] 位会在 digest 中对应位置被置 1。
        """
        if self.digest is not None:
            return self.digest

        self.digest = [0] * 32

        # 根据已处理字节数计算阈值
        if self.count == 3:
            total = 1
        elif self.count == 4:
            total = 4
        elif self.count > 4:
            total = 8 * self.count - 28
        else:
            # 如果不足 3 个字节，可以自定义处理或保持为 0
            total = 0

        threshold = total // 256
        for i in range(256):
            if self.acc[i] > threshold:
                # 为 digest[31 - (i >> 3)] 的 (i & 7) 位置 1
                self.digest[31 - (i >> 3)] += 1 << (i & 7)

        return self.digest

    def hexdigest(self):
        """
        将 32字节(256位)的摘要转换为 64 位十六进制字符串(大写)并返回。
        """
        if self.digest is None:
            self.compute_digest()
        return ''.join(format(x, '02x').upper() for x in self.digest)


def remove_excessive_zeros(payload):
    """
    删除字符串中任意超过 10 个连续 '0' 的部分。
    例如 '00000000000' (11个0) 会被整个删除。
    """
    if isinstance(payload, str):
        return re.sub(r'0{11,}', '', payload)
    return payload


def hex_to_binary(hex_str):
    """
    将 64 位十六进制字符串转换为 256 位二进制字符串（每个16进制字符 => 4个二进制位）。
    """
    # 注意：Nilsimsa hexdigest() 返回的是 64 个 16 进制字符 => 256 bits
    # 这里逐字符转换，每个16进制字符 -> 4 bits
    # 64 * 4bit = 256bit
    return ''.join(format(int(char, 16), '04b') for char in hex_str)


def process_csv_file(input_csv, output_csv):
    """
    读取单个 CSV 文件，对 payload 列做以下处理：
      1) 去除超过 10 个连续 '0'
      2) Nilsimsa 哈希 => 64位 hex
      3) hex -> 256位二进制
      4) 替换原有的 payload
    最后将更新后的 DataFrame 保存到 output_csv。
    """
    df = pd.read_csv(input_csv)

    for idx, row in df.iterrows():
        payload = row.get('payload', None)  # 若无该列，则返回 None
        if isinstance(payload, str) and payload.strip():
            # 1) 去零
            cleaned_payload = remove_excessive_zeros(payload)

            # 2) 计算Nilsimsa哈希 (hex)
            n = Nilsimsa()
            n.update(cleaned_payload.encode('utf-8'))
            hashed_hex = n.hexdigest()

            # 3) 转换为256位二进制
            hashed_bin = hex_to_binary(hashed_hex)

            # 4) 用256位二进制串替换原有 payload
            df.at[idx, 'payload'] = hashed_bin
        else:
            # 如果 payload 为空或 NaN，则用空字符串或其他标识替代
            df.at[idx, 'payload'] = ''

    df.to_csv(output_csv, index=False)
    print(f"已处理并保存: {output_csv}")


def process_all_csv(input_folder, output_folder):
    """
    遍历 input_folder 下的所有子目录及文件，处理每一个 .csv 文件。
    将处理后的文件保存在 output_folder 下对应的路径结构中。
    并统计共处理了多少个 csv 文件。
    """
    file_count = 0

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.csv'):
                file_count += 1  # 统计处理的文件数
                input_csv_path = os.path.join(root, file)

                # 构造输出目录的路径结构（保持相对路径一致）
                relative_path = os.path.relpath(root, input_folder)
                target_dir = os.path.join(output_folder, relative_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                # 输出文件名与原文件名相同
                output_csv_path = os.path.join(target_dir, file)

                # 处理并输出
                process_csv_file(input_csv_path, output_csv_path)

    print(f"\n处理完成！共处理了 {file_count} 个 CSV 文件。")


def main():
    input_folder = '/home/hyj/deviceIdentification/dataset/LabData/15_keyPacketSignature'
    output_folder = '/home/hyj/deviceIdentification/dataset/LabData/16_keyPacketSignatureWithLSH'

    process_all_csv(input_folder, output_folder)
    print("所有文件处理完成！")


if __name__ == "__main__":
    main()
