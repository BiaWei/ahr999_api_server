# ahr999_api_server
Get bitcoin prices from OKX, calculate AHR999 index and provide API access, and can be subscribed and pushed through bark app on iphone
### ahr999_api_server 项目文档

---

#### 1. 项目简介

AHR999 是一个基于 Python 的加密货币价格监控和分析工具，旨在帮助用户跟踪加密货币价格的变化，并根据一定的算法计算出 AHR999 指数，为用户提供参考和决策依据。

---

#### 2. 功能

- **实时价格监控**：监控比特币等加密货币的实时价格变动。启动后自动从okx.com每分钟获取一次BTC-USDT的价格数据并存储，并计算ahr999指数
  
- **AHR999 指数计算**：根据最新价格、200天定投平均成本和指数增长模型，计算出 AHR999 指数。

- **订阅功能**：可以通过Bark App获取当前的ahr999指数，并订阅过去一分钟的价格涨跌幅提醒。

---

#### 3. 功能

```
main.py: 服务器本体，每隔1分钟获取一次ahr999指数并判断是否推送

start.py：设置端口通过uvicorn启动服务器

globals.py：定义全局变量和订阅类
    url_data：send_token接口对应的bark推送信息json，发送bark token后返回一次ahr999指标
        分为消息标题、内容、图标
    price_change_data：价格在一分钟内达到变动阈值的推送信息json
        内容同上
    full_data：ahr999指数的全部信息
            "ahr999": ahr999指数
            "update_time": 上次更新时间%Y-%m-%d %H:%M:%S
            "unix_time": 上次更新的unix时间
            "price": 上次更新的btc价格
            "cost_200day": 用于计算ahr999指数的前200天平均定投成本
            "exp_growth_valuation": 用于计算ahr999指数的指数增长估值
    Subscription类:
        url：str bark app的完整订阅url
        enable_quote_notif：bool 是否开启订阅
        quote_threshold：推送的价格百分比阈值，1.0则为1%

subscription.py：加载与保存订阅信息
    load_subscriptions()：将本地的Subscription加载到全局变量
    save_subscriptions()：将全局变量保存到本地json

server.py：定义api接口
    decode_base64_url(encoded_url: str)：解码base64，api传入的bark url为base64编码
    send_token(encoded_url: str)：GET请求，对服务器发送bark url，服务器收到后返回一次当前ahr999指数
    get_full_data()：GET，返回一次full_data，内容见globals.py
    bark_subscribe(encoded_url: str, enable_quote_notif: bool = Query(...), quote_threshold: float = Query(...))：POST请求订阅，给出base64编码的url、启用订阅bool、提醒阈值百分比
    bark_unsubscribe(encoded_url: str)：POST请求取消订阅，仅给出URL
    get_subscribe_data()：GET请求，直接返回所有用户的订阅信息

ahr999.py：计算ahr999指数相关
    cal_ahr999(current_price, geometric_mean_last_200, predicted_price):通过现价、200天定投平均成本、指数预测价格计算ahr999指数
    predict_price(base_date, get_date)，预测价格，给出当前时间get_date和初始日期base_date，初始日期为int整型，以"2009/01/03"为1计算到当前日期的天数

price.py：从OKX获取BTC-USD现价
    get_btc_price(inst_id, retries=5, delay=5)：inst_id选择BTC-USDT-SWAP，重试retries与重试延迟默认均为5

savedata.py：通过pandas保存价格信息到csv
    write_file_3col(file_path, date, price, ahr999)：写入当日的文件到file_path，名称为%Y-%m-%d，第一列为时间、第二列为价格，第三列为ahr999.如果文件不存在或为空，创建文件并写入数据和索引，文件存在且不为空，追加写入数据，不包含索引和表头
    write_file_4col(file_path, date, price, geometric_mean_price, predicted_price)：第一列为时间%Y-%m-%d，第二列为价格，第三列为要写入的几何平均成本，第四列为预测价格

url_test.py：测试订阅，非必需
    分别测试五个api，可单独运行


```
---

#### 4. 使用说明

##### 安装依赖

```
pip install -r requirements.txt
```

##### 启动服务

```
python start.py
```

##### API 文档

- **获取完整数据**: `/get_full_data` (GET)
- **发送订阅**: `/bark_subscribe` (POST)
- **取消订阅**: `/bark_unsubscribe` (POST)

详细 API 文档请参考 [API 文档](#)。

