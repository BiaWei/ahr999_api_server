import os
import requests

# 配置
API_URL = "https://ahr999.3geeks.top/download/history_price"  # 文件下载的 API 端点
SAVE_DIR = "./data"  # 保存文件的目录
SAVE_FILE_NAME = "price.csv"  # 保存文件的文件名


def download_file(api_url: str, save_dir: str, file_name: str):
    """
    从指定 API 下载文件并保存到指定目录

    :param api_url: 文件下载的 API 地址
    :param save_dir: 文件保存目录
    :param file_name: 文件保存的文件名
    """
    # 创建保存目录（如果不存在）
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 发送 GET 请求
    try:
        print(f"Fetching file from {api_url}...")
        response = requests.get(api_url, stream=True)
        response.raise_for_status()  # 如果返回状态码不是 200，则抛出异常

        # 目标文件路径
        file_path = os.path.join(save_dir, file_name)

        # 保存文件
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):  # 分块读取
                file.write(chunk)

        print(f"File successfully downloaded and saved to {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download file: {e}")

if __name__ == "__main__":
    # 下载文件并保存到指定目录
    download_file(API_URL, SAVE_DIR, SAVE_FILE_NAME)
