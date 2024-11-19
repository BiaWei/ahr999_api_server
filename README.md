# ahr999_api_server

Get bitcoin prices from OKX, calculate the AHR999 index, provide API access, and enable subscription and push notifications via the Bark app on iPhone.

### ahr999_api_server Documentation

---

#### 1. Project Overview

ahr999_api_server is a Python-based cryptocurrency price monitoring and analysis tool designed to help users track cryptocurrency price changes. It calculates the AHR999 index based on specific algorithms, offering users valuable insights for decision-making.

The Bitcoin ahr999 Hoarding Index is an index created by Weibo user ahr999. Its purpose is to assist Bitcoin fixed investment users to make investment decisions in combination with timing strategies. This index combines the short-term fixed investment yield of Bitcoin with the degree of deviation of Bitcoin price from expected valuation, thereby providing more comprehensive market information.
The calculation method is:

$$\frac{\text{spot price}}{\text{200days geometric price}} \times \frac{\text{spot price}}{\text{predicted price}}$$

Where spot_price is the spot price, 200days_geometric_price is the average fixed investment cost (geometric mean) in the past 200 days, and predicted_price is the index prediction valuation;
The predicted_price is a linear regression fit of the coin age (number of days from 2009/1/3) and the logarithm of the past price log(historical_price), and then calculated based on the coin age of the day.

When the ahr999 indicator is less than 0.45, it is the bottom-hunting range, which has appeared in 2022/6, 2022/9, 2022/11, and 2023/9.
When the ahr999 indicator is greater than 0.45 and less than 1.2, it is the fixed investment range;
When the ahr999 indicator is less than 0.45, stop fixed investment and sell in combination with other indicators.

---

#### 2. Features

- **Real-time Price Monitoring**: Monitors real-time price changes of cryptocurrencies like Bitcoin. Once started, it automatically fetches the BTC-USDT price data from OKX every minute, stores it, and calculates the AHR999 index.

- **AHR999 Index Calculation**: Calculates the AHR999 index using the latest price, 200-day average investment cost, and exponential growth model.

- **Subscription Feature**: Allows users to subscribe to the current AHR999 index and receive notifications about price changes over the past minute through the Bark app.

---

#### 3. Functional Modules

```
main.py: The main server script. Fetches the AHR999 index every minute and determines whether to send push notifications.

start.py: Sets up the server and starts it using uvicorn.

globals.py: Defines global variables and the Subscription class. url_data: JSON object for Bark push notification information via the send_token interface. Sends a single AHR999 index when the Bark token is provided. Includes message title, content, and icon. price_change_data: JSON object for push notifications when price change thresholds are reached within a minute. Similar structure to url_data. full_data: Full information about the AHR999 index: - "ahr999": AHR999 index value. - "update_time": Last update time in %Y-%m-%d %H:%M:%S format. - "unix_time": Last update time in UNIX timestamp. - "price": Latest BTC price. - "cost_200day": 200-day average investment cost used for calculating the AHR999 index. - "exp_growth_valuation": Exponential growth valuation for calculating the AHR999 index. Subscription class: - url: str. Full subscription URL for the Bark app. - enable_quote_notif: bool. Whether to enable subscription notifications. - quote_threshold: float. Percentage threshold for price change notifications (e.g., 1.0 represents 1%).

subscription.py: Loads and saves subscription information. load_subscriptions(): Loads Subscription data from local storage into global variables. save_subscriptions(): Saves global Subscription data into a local JSON file.

server.py: Defines API endpoints. decode_base64_url(encoded_url: str): Decodes a base64-encoded Bark URL passed via API. send_token(encoded_url: str): GET request. Sends the current AHR999 index to the provided Bark URL. get_full_data(): GET request. Returns the full_data JSON object. bark_subscribe(encoded_url: str, enable_quote_notif: bool = Query(...), quote_threshold: float = Query(...)): POST request for subscription. Takes a base64-encoded URL, a boolean for enabling notifications, and a percentage threshold for price alerts. bark_unsubscribe(encoded_url: str): POST request to unsubscribe, providing only the URL. get_subscribe_data(): GET request. Returns all subscription information stored on the server.

ahr999.py: Handles AHR999 index calculations. cal_ahr999(current_price, geometric_mean_last_200, predicted_price): Calculates the AHR999 index using the current price, 200-day average investment cost, and exponential growth valuation. predict_price(base_date, get_date): Predicts prices based on the base date and the current date. The base date is an integer starting from "2009/01/03", representing the number of days since that date.

price.py: Fetches the BTC-USDT price from OKX. get_btc_price(inst_id, retries=5, delay=5): Retrieves the BTC-USDT-SWAP price with default retry and delay settings.

savedata.py: Saves price information to a CSV file using pandas. write_daily_file(file_path, date, price, ahr999): Writes daily price and AHR999 data to a file. If the file does not exist or is empty, it creates the file and writes data with headers. If the file exists, appends data without headers or index. write_overall_file(file_path, date, price, geometric_mean_price, predicted_price): Writes overall data, including date, price, geometric mean cost, and predicted price.

test/url_test.py: Subscription testing (optional). Includes test cases for five API endpoints, which can be run independently.
```

---

#### 4. File Structure

```
test/: Test files.

data/: Directory for storing subscription information, daily prices (price at 00:00), and per-minute prices for a single day.

html/: Frontend HTML files rendered via FastAPI.

legacy(useless)/: Deprecated files.
```

---

#### 5. Usage Instructions

##### Install Dependencies

```
pip install -r requirements.txt
```

##### Configuration

```
Modify the server URL in html/index.html to set the server address.

Update server_url in test/url_test.py for testing.

Set bark_url in test/url_test.py to your Bark URL for testing.

Adjust the URLs in MESSAGE_TEMPLATE in notification.py to point to the server address. Clicking on the Bark notification will redirect to the frontend HTML.

```

##### Start the Server

```
python start.py
```
##### API Endpoints


- **Get Full Data**: `/get_full_data` (GET)
- **Fetch Data and Send via Bark**: `/send_token` (GET)
- **Subscribe**: `/bark_subscribe` (POST)
- **Unsubscribe**: `/bark_unsubscribe` (POST)
- **Get All Subscription Data**: `/get_subscribe_data` (GET)




# ahr999_api_server
Get bitcoin prices from OKX, calculate AHR999 index and provide API access, and can be subscribed and pushed through bark app on iphone
### ahr999_api_server 项目文档

---

#### 1. 项目简介

ahr999_api_server 是一个基于 Python 的加密货币价格监控和分析工具，旨在帮助用户跟踪加密货币价格的变化，并根据一定的算法计算出 AHR999 指数，为用户提供参考和决策依据。

比特币ahr999囤币指标是由微博用户ahr999创造的一项指标，其目的是辅助比特币定投用户结合择机策略做出投资决策。 该指标将比特币的短期定投收益率与比特币价格与预期估值的偏离程度结合起来，从而提供了更全面的市场信息。
计算方法为：

$$\frac{\text{spot price}}{\text{200days geometric price}} \times \frac{\text{spot price}}{\text{predicted price}}$$

其中spot_price为现货价格，200days_geometric_price为过去200天的定投平均成本(几何平均数)，predicted_price为指数预测估值；
predicted_price由币龄(从2009/1/3开始到当日的天数)与过去价格的对数log(historical_price)进行线性回归拟合，然后根据当天的币龄计算得出。

ahr999指标在小于0.45时为抄底区间，抄底区间在2022/6、2022/9、2022/11、2023/9均出现过。
ahr999指标大于0.45、小于1.2时为定投区间；
ahr999指标在小于0.45时停止定投，结合其他指标进行卖出。

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
    write_daily_file(file_path, date, price, ahr999)：写入当日的文件到file_path，名称为%Y-%m-%d，第一列为时间、第二列为价格，第三列为ahr999.如果文件不存在或为空，创建文件并写入数据和索引，文件存在且不为空，追加写入数据，不包含索引和表头
    write_overall_file(file_path, date, price, geometric_mean_price, predicted_price)：第一列为时间%Y-%m-%d，第二列为价格，第三列为要写入的几何平均成本，第四列为预测价格

test/url_test.py：测试订阅，非必需
    分别测试五个api，可单独运行


```
---

#### 4. 文件结构

```
test/：测试文件
    
data/：数据目录，分别存储订阅信息、每日价格信息(每天00:00的价格)、单日的每分钟价格

html/：html前端，挂载在fastapi上呈现网页

legacy(useless)/：已弃用
    
```

---

#### 5. 使用说明

##### 安装依赖

```
pip install -r requirements.txt
```

##### 配置

```
修改html/index.html中的url作为服务器地址

修改test/url_test.py中的server_url作为服务器地址，用于测试

修改test/url_test.py中的bark_url为你的bark url，用于测试

修改notification.py中MESSAGE_TEMPLATE的各个url作为服务器地址，在bark发送通知后可点击通知进入前端html
```

##### 启动服务

```
python start.py
```
##### API 文档

- **获取完整数据**: `/get_full_data` (GET)
- **主动获取数据并发送到bark**: `/send_token` (GET)
- **发送订阅**: `/bark_subscribe` (POST)
- **取消订阅**: `/bark_unsubscribe` (POST)
- **获取服务器的所有订阅信息**: `/get_subscribe_data` (GET)



