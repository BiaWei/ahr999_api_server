import threading
import time
import savedata
import price
import os
import pandas as pd
import ahr999 as ahr
from scipy.stats import gmean
from urllib.parse import quote
import globals
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import subscribe  # 导入 subscribe.py 中的函数
import requests  # 导入 requests 模块用于发送 HTTP 请求
import price

app = FastAPI()

# 导入 server.py 中的路由
import server

app.include_router(server.router)

# 存储过去15分钟每分钟的价格和涨跌幅
past_15_min_prices = []

# 存储订阅 URL 的标记信息
url_notifications = {}

app.mount("/static", StaticFiles(directory="data"), name="static")

def update_price_data():
    last_date = "1900/01/01"
    inst_id = "BTC-USDT-SWAP"
    daily_price_path = "data/price.csv"
    today_price_path = "data/historical/" + last_date.replace("/", "-") + ".csv"
    print("init path:", today_price_path)

    # 确保目录存在
    os.makedirs(os.path.dirname(daily_price_path), exist_ok=True)
    os.makedirs(os.path.dirname(today_price_path), exist_ok=True)

    base_date = pd.to_datetime("2009/01/03")

    while True:
        latest_btc_price = price.get_btc_price(inst_id)
        if latest_btc_price is None:
            print("Failed to get the latest BTC price after retries.")
            time.sleep(60)  # Wait before next attempt
            continue

        print("price:", latest_btc_price)

        # 将当前价格加入过去15分钟价格列表
        if len(past_15_min_prices) >= 15:
            past_15_min_prices.pop(0)  # 移除最早的一条数据
        past_15_min_prices.append(float(latest_btc_price))

        # 如果有15分钟前的价格
        if len(past_15_min_prices) == 15:
            price_changes = [(float(latest_btc_price) / price - 1) * 100 for price in past_15_min_prices]
            max_abs_change = max(price_changes, key=abs)
            max_change = max(price_changes)

            print(f"Max absolute price change in past 15 minutes: {max_abs_change:.4f}%")

            # 更新全局数据
            globals.price_change_data['text'] = f"Max price change {max_change:.4f}% in past 15 minutes, the current price is ${float(latest_btc_price)}."

            # 遍历globals.subscriptions每个订阅
            for sub in globals.subscriptions:
                current_time = time.time()
                last_notified = url_notifications.get(sub.url, {}).get("time", 0)
                last_change = url_notifications.get(sub.url, {}).get("change", 0)

                # 15分钟内是否需要发送通知
                if sub.enable_quote_notif and current_time - last_notified < 900:
                    if abs(max_change) > abs(last_change):
                        notification_url = f"{sub.url}{quote(globals.price_change_data['title'])}/{quote(globals.price_change_data['text'])}?icon={globals.price_change_data['icon']}"
                        try:
                            response = requests.get(notification_url)
                            if response.status_code == 200:
                                print(f"Notification sent successfully to {sub.url}")
                                url_notifications[sub.url] = {"time": current_time, "change": max_change}
                            else:
                                print(f"Failed to send notification to {sub.url}, status code: {response.status_code}")
                        except Exception as e:
                            print(f"Error sending notification to {sub.url}: {e}")
                elif sub.enable_quote_notif and abs(max_change) > sub.quote_threshold:
                    # 15分钟后重新发送通知
                    notification_url = f"{sub.url}{quote(globals.price_change_data['title'])}/{quote(globals.price_change_data['text'])}?icon={globals.price_change_data['icon']}"
                    try:
                        response = requests.get(notification_url)
                        if response.status_code == 200:
                            print(f"Notification sent successfully to {sub.url}")
                            url_notifications[sub.url] = {"time": current_time, "change": max_change}
                        else:
                            print(f"Failed to send notification to {sub.url}, status code: {response.status_code}")
                    except Exception as e:
                        print(f"Error sending notification to {sub.url}: {e}")

        # get current time
        get_unix_time = time.time()
        get_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        get_date = get_time[:get_time.find(' ')]
        print("Time:", get_time)

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
                print(f"Geometric mean of the last 200 prices: {geometric_mean_last_200}")
            else:
                geometric_mean_last_200 = None
                print("Not enough data to calculate geometric mean.")

            # 计算预测价格
            predicted_price = ahr.predict_price(base_date, get_date)
            print(f"Predicted price: {predicted_price}")

            last_date = get_date
            today_price_path = "data/historical/" + last_date.replace("/", "-") + ".csv"
            # 写入一次大文件 时间精确到日期
            savedata.write_file_4col(daily_price_path, get_date, latest_btc_price, geometric_mean_last_200,
                                     predicted_price)

        # 每次请求价格后根据geometric_mean_last_200和predicted_price计算当前价格对应的ahr999
        if geometric_mean_last_200 is not None and predicted_price is not None:
            ahr999 = ahr.cal_ahr999(latest_btc_price, geometric_mean_last_200, predicted_price)
            print(f"AHR999 index: {ahr999}")
        else:
            ahr999 = None
            print("Not enough data to calculate AHR999.")

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
