import pandas as pd
from datetime import datetime, timedelta


def fetch_24h_high_low():

    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 或者使用你指定的日期和时间
    # current_datetime = datetime.strptime("2024-06-21 10:00", "%Y-%m-%d %H:%M")

    # 定义文件路径和格式
    file_path = "data/historical"
    file_format = "*.csv"

    # 获取前一天的同一时刻
    previous_datetime = current_datetime - timedelta(days=1)

    # 读取当前日期和前一天的CSV文件
    current_file = f"{file_path}/{current_datetime.strftime('%Y-%m-%d')}.csv"
    previous_file = f"{file_path}/{previous_datetime.strftime('%Y-%m-%d')}.csv"

    # 读取CSV文件
    current_df = pd.read_csv(current_file, parse_dates=["Date"])
    previous_df = pd.read_csv(previous_file, parse_dates=["Date"])

    # 筛选前一天同一时刻之后的数据
    previous_df = previous_df[previous_df["Date"] >= previous_datetime]

    # 合并数据
    combined_df = pd.concat([previous_df, current_df])

    # 计算Price的最大值和最小值
    max_price = combined_df["Price"].max()
    min_price = combined_df["Price"].min()

    print(f"Max: {max_price}")
    print(f"Min: {min_price}")

    return max_price, min_price

# fetch_24h_high_low()