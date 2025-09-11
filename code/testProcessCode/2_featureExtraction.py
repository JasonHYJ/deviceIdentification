# -- coding: utf-8 --

"""
本文件使用tshark对保留的文件夹suitableDir下的所有pcap文件中提取相应的特征信息保存到目标csv文件目录下
并且根据设备的MAC地址判断数据包的方向，方向为1表示从设备发出的包，方向为-1表示从云端返回的包。
实现的功能：
1、遍历指定目录下的 .pcap 文件。
2、使用 tshark 工具从每个 .pcap 文件中提取特征信息，并保存到对应的 .csv 文件中。
3、根据设备的 MAC 地址，判断数据包的方向（设备发送为 1，设备接收为 -1），并将方向特征添加到 .csv 文件中。
4、为每个数据包添加时间间隔
"""

import os
import subprocess
import shlex
import csv

# 设备 MAC 地址字典，将设备名称与其对应的 MAC 地址进行映射
device_mac_mapping = {
    # uk数据集
    "uk_allure-speaker": "b0:f1:ec:d4:26:ae",
    "uk_appletv": "50:32:37:b8:c7:0f",
    "uk_blink-security-hub": "00:03:7f:96:d8:ec",
    "uk_bosiwo-camera-wifi": "00:0c:43:03:51:be",
    "uk_bosiwo-camera-wired": "ae:ca:06:0e:ec:89",
    "uk_charger-camera": "fc:ee:e6:2e:23:a3",
    "uk_echodot": "cc:f7:35:49:f4:05",
    "uk_echoplus": "00:fc:8b:84:22:10",
    "uk_echospot": "5c:41:5a:29:ad:97",
    "uk_firetv": "cc:f7:35:25:af:4d",
    "uk_google-home": "54:60:09:6f:32:84",
    "uk_google-home-mini": "20:df:b9:13:e5:2e",
    "uk_honeywell-thermostat": "b8:2c:a0:28:3e:6b",
    "uk_lightify-hub": "84:18:26:7c:1a:56",
    "uk_magichome-strip": "dc:4f:22:89:fc:e7",
    "uk_nest-tstat": "64:16:66:2a:98:62",
    "uk_netatmo-weather-station": "70:ee:50:36:98:da",
    "uk_ring-doorbell": "f0:45:da:36:e6:23",
    "uk_roku-tv": "c8:3a:6b:fa:1c:00",
    "uk_samsungtv-wired": "fc:03:9f:93:22:62",
    "uk_sengled-hub": "b0:ce:18:20:43:bf",
    "uk_smarter-coffee-mach": "0c:2a:69:11:01:ba",
    "uk_smartthings-hub": "d0:52:a8:a4:e6:46",
    "uk_sousvide": "68:c6:3a:ba:c2:6b",
    "uk_t-philips-hub": "ec:b5:fa:00:98:da",
    "uk_t-wemo-plug": "58:ef:68:99:7d:ed",
    "uk_tplink-bulb": "50:c7:bf:ca:3f:9d",
    "uk_tplink-plug": "50:c7:bf:b1:d2:78",
    "uk_tplink-plug2": "b0:be:76:be:f2:aa",
    "uk_xiaomi-cam2": "78:11:dc:76:69:b0",
    "uk_xiaomi-cleaner": "78:11:dc:ec:a3:ab",
    "uk_xiaomi-hub": "7c:49:eb:88:da:82",
    "uk_xiaomi-plug": "7c:49:eb:22:30:9c",
    "uk_yi-camera": "0c:8c:24:0b:be:fb",

    # us数据集
    "us_amcrest-cam-wired": "9c:8e:cd:0a:33:1b",
    "us_appletv": "08:66:98:a2:21:9e",
    "us_blink-security-hub": "00:03:7f:4f:c6:b5",
    "us_brewer": "20:f8:5e:cc:18:1f",
    "us_bulb1": "ec:fa:bc:82:20:bb",
    "us_cloudcam": "b0:fc:0d:c9:00:4c",
    "us_dlink-mov": "6c:72:20:c5:0a:3f",
    "us_dryer": "c0:97:27:73:aa:38",
    "us_echodot": "18:74:2e:41:4d:35",
    "us_echoplus": "fc:a1:83:38:e0:2d",
    "us_echospot": "00:71:47:c0:91:93",
    "us_firetv": "6c:56:97:35:39:f4",
    "us_fridge": "70:2c:1f:3b:36:53",
    "us_google-home-mini": "20:df:b9:5f:41:7e",
    "us_google-home-mini2": "44:07:0b:50:4d:df",
    "us_ikettle": "0c:2a:69:0e:91:16",
    "us_insteon-hub": "00:0e:f3:3b:85:e5",
    "us_invoke": "d8:f7:10:c3:34:e4",
    "us_lefun-cam-wired": "ae:ca:06:08:d3:e6",
    "us_lgtv-wired": "38:8c:50:68:d7:5c",
    "us_lightify-hub": "84:18:26:7d:cf:a2",
    "us_luohe-spycam": "00:0c:43:20:32:bb",
    "us_magichome-strip": "dc:4f:22:c1:58:05",
    "us_microseven-camera": "00:fc:5c:e0:81:86",
    "us_microwave": "d8:28:c9:10:b5:60",
    "us_nest-tstat": "18:b4:30:c8:d8:28",
    "us_philips-bulb": "34:ce:00:99:9b:83",
    "us_ring-doorbell": "98:84:e3:e4:35:bd",
    "us_roku-tv": "88:de:a9:08:03:b9",
    "us_samsungtv-wired": "84:c0:ef:2f:42:cc",
    "us_sengled-hub": "b0:ce:18:27:9f:e4",
    "us_smartthings-hub": "24:fd:5b:04:1b:75",
    "us_sousvide": "dc:4f:22:28:b6:5b",
    "us_t-echodot": "fc:65:de:5f:15:0a",
    "us_t-philips-hub": "00:17:88:68:5f:61",
    "us_t-smartthings-hub": "24:fd:5b:02:1d:3a",
    "us_t-wemo-plug": "14:91:82:b4:4b:5f",
    "us_tplink-bulb": "50:c7:bf:a0:f3:76",
    "us_tplink-plug": "50:c7:bf:5a:2e:a0",
    "us_washer": "c0:97:27:81:67:99",
    "us_wink-hub2": "00:21:cc:4d:ce:8c",
    "us_xiaomi-hub": "34:ce:00:83:99:35",
    "us_xiaomi-ricecooker": "7c:49:eb:35:7a:49",
    "us_xiaomi-strip": "34:ce:00:8b:22:74",
    "us_yi-camera": "b0:d5:9d:b9:f0:b4",
    "us_zmodo-doorbell": "7c:c7:09:56:6e:48",

    # ciciot数据集
    "ciciot_AmazonAlexaEchoDot1": "1c:fe:2b:98:16:dd",
    "ciciot_AmazonAlexaEchoDot2": "a0:d0:dc:c4:08:ff",
    "ciciot_AmazonAlexaEchoSpot": "1c:12:b0:9b:0c:ec",
    "ciciot_AmazonAlexaEchoStudio": "08:7c:39:ce:6e:2a",
    "ciciot_AmazonPlug": "b8:5f:98:d0:76:e6",
    "ciciot_AMCREST-WiFiCamera": "9c:8e:cd:1d:ab:9f",
    "ciciot_ArloBaseStation": "3c:37:86:6f:b9:51",
    "ciciot_ArloQCamera": "40:5d:82:35:14:c8",
    "ciciot_AtomiCoffeeMaker": "68:57:2d:56:ac:47",
    "ciciot_Borun-Sichuan-AICamera": "c0:e7:bf:0a:79:d1",
    "ciciot_D-LinkDCHS-161WaterSensor": "f0:b4:d2:f9:60:95",
    "ciciot_DCS8000LHA1D-LinkMiniCamera": "b0:c5:54:59:2e:99",
    "ciciot_EufyHomeBase2": "8c:85:80:6c:b6:47",
    "ciciot_GlobeLampESP_B1680C": "50:02:91:b1:68:0c",
    "ciciot_GoogleNestMini": "cc:f4:11:9c:d0:00",
    "ciciot_GosundESP_032979Plug": "b8:f0:09:03:29:79",
    "ciciot_GosundESP_039AAFSocket": "b8:f0:09:03:9a:af",
    "ciciot_GosundESP_0C3994Plug": "c4:dd:57:0c:39:94",
    "ciciot_GosundESP_10098FSocket": "50:02:91:10:09:8f",
    "ciciot_GosundESP_10ACD8Plug": "50:02:91:10:ac:d8",
    "ciciot_GosundESP_147FF9Plug": "24:a1:60:14:7f:f9",
    "ciciot_GosundESP_1ACEE1Socket": "50:02:91:1a:ce:e1",
    "ciciot_HeimVisionSmartLifeRadio-Lamp": "d4:a6:51:30:64:b7",
    "ciciot_HeimVisionSmartWiFiCamera": "44:01:bb:ec:10:4a",
    "ciciot_HomeEyeCamera": "34:75:63:73:f3:36",
    "ciciot_iRobotRoomba": "50:14:79:37:80:18",
    "ciciot_LGSmartTV": "ac:f1:08:4e:00:82",
    "ciciot_LuoheCamDog": "7c:a7:b0:cd:18:32",
    "ciciot_NestIndoorCamera": "44:bb:3b:00:39:07",
    "ciciot_NetatmoCamera": "70:ee:50:68:0e:32",
    "ciciot_NetatmoWeatherStation": "70:ee:50:6b:a8:1a",
    "ciciot_PhilipsHueBridge": "00:17:88:60:d6:4f",
    "ciciot_RingBaseStationAC": "b0:09:da:3e:82:6c",
    "ciciot_SIMCAM1SAMPAKTec": "10:2c:6b:1b:43:be",
    "ciciot_SmartBoard": "00:02:75:f6:e3:cb",
    "ciciot_SonosOneSpeaker": "48:a6:b8:f9:1b:88",
    "ciciot_TeckinPlug1": "d4:a6:51:76:06:64",
    "ciciot_TeckinPlug2": "d4:a6:51:78:97:4e",
    "ciciot_YutronPlug1": "d4:a6:51:20:91:d1",
    "ciciot_YutronPlug2": "d4:a6:51:21:6c:29",

    # unsw数据集
    "unsw_Amazon-Echo": "44:65:0d:56:cc:d3",
    "unsw_Android-Phone": "40:f3:08:ff:1e:da",
    "unsw_Android-Phone2": "b4:ce:f6:a7:a3:c2",
    "unsw_BelkinWemoMotionSensor": "ec:1a:59:83:28:11",
    "unsw_BelkinWemoSwitch": "ec:1a:59:79:f4:89",
    "unsw_BlipcareBloodPressureMeter": "74:6a:89:00:2e:25",
    "unsw_Dropcam": "30:8c:fb:b6:ea:45",
    "unsw_HP-Printer": "70:5a:0f:e4:9b:c0",
    "unsw_iHome": "74:c6:3b:29:d7:1d",
    "unsw_InsteonCamera": "00:62:6e:51:27:2e",
    "unsw_IPhone": "d0:a6:37:df:a1:e1",
    "unsw_Laptop": "74:2f:68:81:69:42",
    "unsw_LiFX-Bulb": "d0:73:d5:01:83:08",
    "unsw_MacBook": "ac:bc:32:d4:6f:2f",
    "unsw_MacBook-Iphone": "f4:5c:89:93:cc:85",
    "unsw_NEST-ProtectSmokeAlarm": "18:b4:30:25:be:e4",
    "unsw_NestDropcam": "30:8c:fb:b6:ea:45",
    "unsw_NetatmoWeatherStation": "70:ee:50:03:b8:ac",
    "unsw_NetatmoWelcome": "70:ee:50:18:34:43",
    "unsw_PIX-STAR-Photo-frame": "e0:76:d0:33:bb:85",
    "unsw_SamsungGalaxyTab": "08:21:ef:3b:fc:e3",
    "unsw_SamsungSmartCam": "00:16:6c:ab:6b:88",
    "unsw_SmartThings": "d0:52:a8:00:67:5e",
    "unsw_TP-LinkDayNightCloudCamera": "f4:f2:6d:93:51:f1",
    "unsw_TP-LinkSmartPlug": "50:c7:bf:00:56:39",
    "unsw_TribySpeaker": "18:b7:9e:02:20:44",
    "unsw_WithingsAuraSmartSleepSensor": "00:24:e4:20:28:c6",
    "unsw_WithingsSmartBabyMonitor": "00:24:e4:11:18:a8",
    "unsw_WithingsSmartScale": "00:24:e4:1b:6f:96",

    # lab数据集
    "lab_HaiqueH1-ipc": "fc:6b:f0:2a:d1:2f",
    "lab_HonorSpeaker": "4c:d1:a1:42:e4:ce",
    "lab_HuaweiSpeaker": "20:da:22:31:25:a6",
    "lab_Tp-linkCamIpc-64c": "48:0e:ec:f2:fe:5d",
    "lab_xiaomi-ipc": "44:23:7c:91:de:f4",
    "lab_Xiaomi-ipcYuntai": "44:23:7c:96:3a:22",
    "lab_XiaomiGateway": "7c:49:eb:b3:ca:5e",
    "lab_XiaomiLamp": "40:31:3c:51:9f:71",
    "lab_XiaomiLamp-1s": "40:31:3c:4e:e9:50",
    "lab_XiaomiSpeaker": "ec:41:18:6a:ab:6c",
    "lab_XiaomiSpeakerPlay": "50:d2:f5:a9:de:5b",
}


def extract_features_from_pcap(source_root, destination_root, device_mac_mapping):
    """
    从 pcap 文件中提取特征信息，计算每个数据包与前一个数据包的时间间隔，并将结果保存为 CSV 文件。

    Parameters:
    source_root (str): 原始 pcap 文件所在的根目录。
    destination_root (str): 保存生成的 CSV 文件的根目录。
    device_mac_mapping (dict): 设备名称与 MAC 地址的映射字典。
    """
    a = 0
    for root, dirs, files in os.walk(source_root, topdown=False):
        for name in files:
            if name.endswith('.pcap'):
                file_name = os.path.join(root, name)

                # 生成对应的 CSV 文件名
                csv_name = name.replace('.pcap', '.csv')

                # 构建目标目录结构
                relative_path = os.path.relpath(root, source_root)  # 计算相对路径
                destination_dir = os.path.join(destination_root, relative_path)
                os.makedirs(destination_dir, exist_ok=True)  # 创建新目录

                destination_csv = os.path.join(destination_dir, csv_name)

                print(f"Processing {file_name} -> {destination_csv}")

                # 构建 tshark 命令，添加 MAC 和 IP 地址的提取
                command = (
                    'tshark -r ' + shlex.quote(file_name) +
                    ' -T fields -e frame.time_epoch -e frame.protocols -e frame.len -e eth.src -e eth.dst ' +
                    '-e ip.src -e ip.dst -e ip.len -e tcp.len -e udp.length -e ip.ttl -e tcp.srcport -e tcp.dstport ' +
                    '-e udp.srcport -e udp.dstport -e tcp.flags -e tls.record.content_type -e tcp.window_size ' +
                    '-e _ws.expert.message -e tcp.payload -e udp.payload ' +
                    '-E header=y -E separator=, -E quote=d -E occurrence=f > ' +
                    shlex.quote(destination_csv)
                )
                print(command)

                # 使用 subprocess 执行命令
                subprocess.run(command, shell=True, check=True)

                # 添加时间间隔和方向特征
                temp_csv = destination_csv + ".temp"
                with open(destination_csv, 'r') as infile, open(temp_csv, 'w', newline='') as outfile:
                    reader = csv.reader(infile)
                    writer = csv.writer(outfile)

                    headers = next(reader)
                    headers.append('direction')  # 新增方向特征列
                    headers.append('time_interval')  # 新增时间间隔列
                    writer.writerow(headers)

                    prev_time = None
                    for row in reader:
                        src_mac = row[3]  # eth.src
                        dst_mac = row[4]  # eth.dst
                        direction = 0

                        # 遍历字典，找到匹配的 MAC 地址并判断方向
                        for device, mac_address in device_mac_mapping.items():
                            if src_mac == mac_address:
                                direction = 1  # 该设备发送
                            elif dst_mac == mac_address:
                                direction = -1  # 该设备接收

                        # 计算时间间隔
                        curr_time = float(row[0])  # frame.time_epoch
                        if prev_time is None:
                            time_interval = 0  # 第一个包没有时间间隔
                        else:
                            time_interval = curr_time - prev_time
                        prev_time = curr_time

                        row.append(str(direction))
                        row.append(f"{time_interval:.6f}")
                        writer.writerow(row)

                # 替换旧的 CSV 文件
                os.replace(temp_csv, destination_csv)

                # 打印进度
                print(a)
                a += 1


def main():
    # 定义源目录和目标目录
    source_directory = "/home/hyj/deviceIdentification/dataset/testData/LabData/splitByPeriod"
    destination_directory = "/home/hyj/deviceIdentification/dataset/testData/LabData/featureCsv"

    # 调用函数提取特征
    extract_features_from_pcap(source_directory, destination_directory, device_mac_mapping)


if __name__ == "__main__":
    main()
