# AHR999 API Server

[English Version](https://github.com/BiaWei/ahr999_api_server/blob/main/README.md) | [简体中文](https://github.com/BiaWei/ahr999_api_server/blob/main/README.zh.md)

---

### 1. 项目简介

`ahr999_api_server` 是一个基于 Python 的加密货币价格监控和分析工具，旨在帮助用户跟踪加密货币价格的变化，并根据一定的算法计算出 AHR999 指数，为用户提供参考和决策依据。

比特币ahr999囤币指标是由微博用户ahr999创造的一项指标，其目的是辅助比特币定投用户结合择机策略做出投资决策。该指标将比特币的短期定投收益率与比特币价格与预期估值的偏离程度结合起来，从而提供了更全面的市场信息。

**计算方法**：

$$
ahr999 = \frac{\text{spot price}}{\text{200days geometric price}} \times \frac{\text{spot price}}{\text{predicted price}}
$$

- **spot price**: 现货价格
- **200days geometric price**: 过去200天的定投平均成本（几何平均数）
- **predicted price**: 指数预测估值，基于币龄与历史价格的对数进行线性回归拟合

**指数解释**：
- **ahr999 < 0.45**：抄底区间，曾在2022/6、2022/9、2022/11、2023/9出现过。
- **0.45 < ahr999 < 1.2**：定投区间
- **1.2 < ahr999**：停止定投，结合其他指标进行卖出。

---

### 2. 功能

- **实时价格监控**：每分钟从 `okx.com` 获取 BTC-USDT 价格数据并存储，同时计算 AHR999 指数。
- **AHR999 指数计算**：根据最新价格、200天定投平均成本和指数增长模型，计算 AHR999 指数。
- **订阅功能**：通过 Bark App 获取 AHR999 指数和价格涨跌幅提醒。

---

### 3. 代码结构

#### `main.py`
服务器本体，每隔1分钟获取一次 AHR999 指数并判断是否推送。

#### `start.py`
设置端口并通过 `uvicorn` 启动服务器。

#### `globals.py`
定义全局变量和订阅类：
- **full_data**：AHR999 指数的全部信息
- **Subscription类**：包含订阅URL、是否启用订阅和推送价格阈值等

#### `subscription.py`
加载与保存订阅信息：
- `load_subscriptions()`: 加载本地订阅信息
- `save_subscriptions()`: 保存订阅信息到本地 JSON 文件

#### `server.py`
定义 API 接口：
- **`/get_full_data`**: 返回完整数据（GET）
- **`/send_token`**: 获取并发送 AHR999 指数（GET）
- **`/bark_subscribe`**: 订阅 API（POST）
- **`/bark_unsubscribe`**: 取消订阅 API（POST）

#### `ahr999.py`
计算 AHR999 指数相关的函数：
- `cal_ahr999()`: 计算 AHR999 指数
- `predict_price()`: 预测价格

#### `price.py`
从 OKX 获取 BTC-USD 现价。

#### `savedata.py`
通过 pandas 保存价格信息到 CSV 文件。

#### `test/url_test.py`
测试订阅功能，非必需。

#### `sync.py`
同步历史数据。

---

### 4. 文件结构

test/ # 测试文件
data/ # 数据目录
    └── subscriptions.json # 订阅信息
    └── price.csv # 每日价格信息
    └── historical/ # 单日的每分钟价格
html/ # 前端 HTML
legacy/ # 已弃用

---

### 5. 使用说明

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置

- 修改html/index.html中的url作为服务器地址

- 修改test/url_test.py中的server_url作为服务器地址，用于测试

- 修改test/url_test.py中的bark_url为你的bark url，用于测试

- 修改notification.py中MESSAGE_TEMPLATE的各个url作为服务器地址，在bark发送通知后可点击通知进入前端html

- 如果你clone下了这个repo但没有过去几天的历史价格，你可以使用`sync.py`从我的服务器下载

#### 启动服务

```
python start.py
```

#### API 文档


- **获取完整数据**: /get_full_data (GET)

**Method**: GET
**描述**: 获取服务器最新的完整数据，包括 AHR999 指数、价格、更新时间等
**参数**: 无
**返回示例**:

```json
{
    "ahr999": "1.234",
    "update_time": "2024-01-01 12:34:56",
    "unix_time": "1704096896000",
    "price": "80000",
    "cost_200day": "65000",
    "exp_growth_valuation": "90000"
}
```
- **主动获取数据并发送到bark**: /send_token (GET)

**Method**: GET
**描述**: 手动触发获取最新数据并通过Bark推送通知
**参数**:

encoded_url: Base64编码的Bark推送URL


返回示例:

```json
{
    "message": "Notification sent successfully",
    "status_code": 200
}
```
- **发送订阅**: /bark_subscribe (POST)

**Method**: POST
**描述**: 订阅Bark推送服务
**参数**:

encoded_url: Base64编码的Bark推送URL，URL格式为"http://aa.bb.cc/xxxxxxxx/"
enable_quote_notif: 是否启用价格通知（布尔值）
quote_threshold: 价格变动阈值（浮点数）


返回示例:

```json
{
    "message": "Subscribe successfully", 
    "status_code": 200
}
```
- **取消订阅**: /bark_unsubscribe (POST)

**Method**: POST
**描述**: 取消Bark推送订阅
**参数**:

encoded_url: Base64编码的Bark推送URL，URL格式为"http://aa.bb.cc/xxxxxxxx/"


返回示例:

```json
{
    "message": "Unsubscribe successful", 
    "status_code": 200
}
```


- **通过价格计算AHR999**： /cal_ahr999

**Method**: GET
**描述**: 根据输入的比特币价格计算AHR999指数
**参数**:

price: 比特币价格（浮点数）


返回示例:

```json
{
    "ahr999": 1.2345
}
```
- **通过AHR999计算价格** /cal_price

**Method**: GET
**描述**: 根据AHR999指数计算对应的比特币价格
**参数**:

ahr999: AHR999指数（浮点数）


返回示例:

```json
{
    "price": 42000.0
}
```
- **注意事项**

- 所有涉及Bark推送的接口都需要对Bark URL进行Base64编码
- 接口返回的状态码和消息可以帮助判断请求是否成功
- 订阅接口支持更新已存在的订阅信息

