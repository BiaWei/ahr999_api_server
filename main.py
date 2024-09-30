import logging
import os
import sys
import threading
import time
import requests  # 导入 requests 模块用于发送 HTTP 请求
import pandas as pd

from urllib.parse import quote
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from scipy.stats import gmean
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import ahr999 as ahr
import globals
import price
import savedata
import server
import subscribe  # 导入 subscribe.py 中的函数

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI()
app.include_router(server.router)
app.mount("/static", StaticFiles(directory="data"), name="static")
app.mount("/html", StaticFiles(directory="html"), name="static")

# 允许所有来源的CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def send_price_change_notification(price_change, latest_btc_price, ahr999, url):
    change_sign = "+" if price_change > 0 else ""
    globals.price_change_data[
        'text'] = f"Max price change {change_sign}{price_change:.4f}% in past 15 minutes, the current price is ${float(latest_btc_price)}, ahr999 is {ahr999:.4f}."
    notification_url = f"{url}{quote(globals.price_change_data['title'])}/{quote(globals.price_change_data['text'])}?icon={globals.price_change_data['icon']}&group=ahr999Server"
    try:
        response = requests.get(notification_url)
        if response.status_code == 200:
            logger.info(f"Notification sent successfully to {url[:-10] + 'XXXXXXXXXX'}")
        else:
            logger.error(f"Failed to send notification to {url[:-10] + 'XXXXXXXXXX'}, status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending notification to {url[:-10] + 'XXXXXXXXXX'}: {e}")


def update_price_data():
    # 初始化
    last_date = "1900/01/01"
    inst_id = "BTC-USDT-SWAP"

    # 定义数据文件夹
    daily_price_path = "data/price.csv"
    today_price_path = "data/historical/" + last_date.replace("/", "-") + ".csv"
    logger.info(f"Init path: {today_price_path}")

    # 确保目录存在
    os.makedirs(os.path.dirname(daily_price_path), exist_ok=True)
    os.makedirs(os.path.dirname(today_price_path), exist_ok=True)

    # 计算币龄天数
    base_date = pd.to_datetime("2009/01/03")

    while True:
        # 获取当前btc价格
        latest_btc_price = price.get_btc_price(inst_id)
        if latest_btc_price is None:
            logger.error("Failed to get the latest BTC price after retries.")
            time.sleep(3)  # Wait before next attempt
            continue

        logger.info(f"price: {latest_btc_price}")

        # get current time
        get_unix_time = time.time()
        get_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        get_date = get_time[:get_time.find(' ')]
        logger.info(f"Time: {get_time}")

        # 读取daily_price_path中最后一个geometric_mean_last_200和predicted_price 用于计算ahr999
        try:
            data = pd.read_csv(daily_price_path)
            geometric_mean_last_200 = float(data['Geometric Mean Price'].iloc[-1])
            predicted_price = float(data['Predicted Price'].iloc[-1])
        except (FileNotFoundError, IndexError, KeyError, ValueError) as e:
            geometric_mean_last_200 = None
            predicted_price = None

        # new day?
        if get_date != last_date:
            # 读取daily_price_path，取第一列日期放入all_date变量
            data = pd.read_csv(daily_price_path)

            # 取第二列所有数据放入all_price变量，header除外
            all_price = data.iloc[:, 1].astype(float)  # 转换为浮点数类型

            # 取all_price最后200个数据放入last_200_price变量
            last_200_price = all_price.iloc[-200:]

            # 计算最后200个价格数据的几何平均值
            if len(last_200_price) > 0:
                geometric_mean_last_200 = gmean(last_200_price)
                logger.info(f"Geometric mean of the last 200 prices: {geometric_mean_last_200}")
            else:
                geometric_mean_last_200 = None
                logger.error("Not enough data to calculate geometric mean.")

            # 计算预测价格
            predicted_price = ahr.predict_price(base_date, get_date)
            logger.info(f"Predicted price: {predicted_price}")

            last_date = get_date
            today_price_path = "data/historical/" + last_date.replace("/", "-") + ".csv"
            # 写入一次大文件 时间精确到日期
            savedata.write_file_4col(daily_price_path, get_date, latest_btc_price, geometric_mean_last_200,
                                     predicted_price)

        # 每次请求价格后根据geometric_mean_last_200和predicted_price计算当前价格对应的ahr999
        if geometric_mean_last_200 is not None and predicted_price is not None:
            ahr999 = ahr.cal_ahr999(latest_btc_price, geometric_mean_last_200, predicted_price)
            logger.info(f"AHR999 index: {ahr999}")
        else:
            ahr999 = None
            logger.error("Not enough data to calculate AHR999.")

        # 创建新的小文件 写入操作包含创建操作 时间精确到秒
        savedata.write_file_3col(today_price_path, get_time, latest_btc_price, ahr999)

        # 刷新待发送消息 get_time中的/换为- 免得bark出错 其他部分不变
        globals.url_data["text"] = f"AHR999: {ahr999:.4f}\r\nLast update: {get_time.replace('/', '-')}"

        # 批量更新 full_data
        globals.full_data.update({
            "ahr999": ahr999,
            "update_time": get_time,
            "unix_time": get_unix_time,
            "price": float(latest_btc_price),
            "cost_200day": float(geometric_mean_last_200) if geometric_mean_last_200 is not None else None,
            "exp_growth_valuation": float(predicted_price) if predicted_price is not None else None
        })

        # 根据subscription发送通知
        for sub in globals.subscriptions:

            # 是否开启通知
            logger.info(f"{sub.url[:-10] + 'XXXXXXXXXX'} notification: {sub.enable_quote_notif}")
            if not sub.enable_quote_notif:
                continue

            # 存储过去15分钟的价格到一个变量中，舍弃超过15分钟的价格
            if len(sub.last_send_price) >= 15:
                sub.last_send_price.pop(0)  # 移除最早的一条数据
            sub.last_send_price.append(float(latest_btc_price))
            logger.info(f"Update price list of {sub.url[:-10] + 'XXXXXXXXXX'}: {sub.last_send_price}")

            for btc_price in sub.last_send_price:
                price_change = (float(latest_btc_price) / btc_price - 1) * 100
                if abs(price_change) > sub.quote_threshold:
                    logger.info(f"Price change reaches threshold, sending to {sub.url[:-10] + 'XXXXXXXXXX'}")
                    send_price_change_notification(price_change, latest_btc_price, ahr999, sub.url)
                    sub.last_send_price = []
                    break

        logger.info("---------------------------------------------------")
        time.sleep(60)


# 启动时加载订阅数据
subscribe.load_subscriptions()

# 启动后台线程
update_thread = threading.Thread(target=update_price_data)
update_thread.daemon = True
update_thread.start()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=11451)
