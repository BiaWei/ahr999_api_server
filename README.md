# AHR999 API Server

[English Version](https://github.com/BiaWei/ahr999_api_server/blob/main/README.md) | [简体中文](https://github.com/BiaWei/ahr999_api_server/blob/main/README.zh.md)

### ahr999_api_server Documentation

---

#### 1. Project Overview

ahr999_api_server is a Python-based cryptocurrency price monitoring and analysis tool designed to help users track cryptocurrency price changes. It calculates the AHR999 index based on specific algorithms, offering users valuable insights for decision-making.

The Bitcoin ahr999 Hoarding Index is an index created by Weibo user ahr999. Its purpose is to assist Bitcoin fixed investment users to make investment decisions in combination with timing strategies. This index combines the short-term fixed investment yield of Bitcoin with the degree of deviation of Bitcoin price from expected valuation, thereby providing more comprehensive market information.
The calculation method is:

$$ahr999=\frac{\text{spot price}}{\text{200days geometric price}} \times \frac{\text{spot price}}{\text{predicted price}}$$

Where ${\text{spot price}}$ is the spot price, $\text{200days geometric price}$ is the average fixed investment cost (geometric mean) in the past 200 days, and $\text{predicted price}$ is the exponential prediction valuation;
The $\text{predicted price}$ is a linear regression fit of the coin age (number of days from 2009/1/3) and the logarithm of the past price $\log_{}{\text{(historical price)}}$, and then calculated based on the coin age of the day.


- **ahr999 < 0.45**：Bottom-hunting range, which has appeared in 2022/6, 2022/9, 2022/11, and 2023/9.
  
- **0.45 < ahr999 < 1.2**：Fixed investment range;

- **1.2 < ahr999**：Stop fixed investment and sell in combination with other indicators.

---

#### 2. Features

- **Real-time Price Monitoring**: Monitors real-time price changes of Bitcoin. Once started, it automatically fetches the BTC-USDT price data from OKX every minute and records it.

- **AHR999 Index Calculation**: Calculates the AHR999 index using the latest price, 200-day average investment cost, and exponential growth model.

- **Subscription Feature**: Allows users to subscribe to the current AHR999 index and receive notifications about price changes over the past minute through the Bark app on iPhone.

---

#### 3. Functional Modules

```
main.py: The main server script.
    Fetches the AHR999 index every minute and determines whether to send push notifications.

start.py:
    Sets up the server and starts it using uvicorn.

globals.py:
    Defines global variables and the Subscription class.
    price_change_data: JSON object for push notifications when price change thresholds are reached within a minute. Similar structure to url_data. 
    full_data: Full information about the AHR999 index:
        "ahr999": AHR999 index value.
        "update_time": Last update time in %Y-%m-%d %H:%M:%S format. 
        "unix_time": Last update time in UNIX timestamp.
        "price": Latest BTC price.
        "cost_200day": 200-day average investment cost used for calculating the AHR999 index.
        "exp_growth_valuation": Exponential growth valuation for calculating the AHR999 index.
        
         
    Subscription class:
    url: str. Full subscription URL for the Bark app.
    enable_quote_notif: bool. Whether to enable subscription notifications.
    quote_threshold: float. Percentage threshold for price change notifications (e.g., 1.0 represents 1%).

subscription.py: Loads and saves subscription information.
    load_subscriptions(): Loads Subscription data from local storage into global variables.
    save_subscriptions(): Saves global Subscription data into a local JSON file.

server.py: Defines API endpoints.
    decode_base64_url(encoded_url: str): Decodes a base64-encoded Bark URL passed via API.
    send_token(encoded_url: str): GET request. Sends the current AHR999 index to the provided Bark URL.
    get_full_data(): GET request. Returns the full_data JSON object.
    bark_subscribe(encoded_url: str, enable_quote_notif: bool = Query(...), quote_threshold: float = Query(...)): POST request for subscription. Takes a base64-encoded URL, a boolean for enabling notifications, and a percentage threshold for price alerts.
    bark_unsubscribe(encoded_url: str): POST request to unsubscribe, providing only the URL.
    get_subscribe_data(): GET request. Returns all subscription information stored on the server.
    cal_price(ahr999: float): estimate price based on given ahr999, today's growth evaluation and average fixed investment cost in past 200 days.
    cal_ahr999(price: float): estimate ahr999 based on given price, today's growth evaluation and average fixed investment cost in past 200 days.

ahr999.py: Handles AHR999 index calculations.
    cal_ahr999(current_price, geometric_mean_last_200, predicted_price): Calculates the AHR999 index using the current price, 200-day average investment cost, and exponential growth valuation.
    predict_price(base_date, get_date): Predicts prices based on the base date and the current date. The base date is an integer starting from "2009/01/03", representing the number of days since that date.

price.py: Fetches the BTC-USDT price from OKX.
    get_btc_price(inst_id, retries=5, delay=5): Fetches the BTC-USDT-SWAP price with retry and delay settings.

savedata.py: Saves price information to a CSV file using pandas.
    write_daily_file(file_path, date, price, ahr999): Writes daily price and AHR999 data to a file. If the file does not exist or is empty, it creates the file and writes data with headers. If the file exists, appends data without headers or index. write_overall_file(file_path, date, price, geometric_mean_price, predicted_price): Writes overall data, including date, price, geometric mean cost, and predicted price.

test/url_test.py: Subscription testing (optional). Includes test cases for five API endpoints, which can be run independently.


```

---

#### 4. File Structure

```
test/: Test files.

data/: Directory for storing subscription information(subscriptions.json), daily prices (price at 00:00)(price.csv), and per-minute prices for a single day (historical/yyyy-mm-dd.csv).

html/: Frontend HTML files served by FastAPI.

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

Adjust the URLs in MESSAGE_TEMPLATE in notification.py to point to the server address. Clicking the Bark notification on your iPhone will redirect to the frontend HTML.

When you clone this repo, you don't have the price data of today to calculate average cost in past 200 days. Use `sync.py` to download data from my server.

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
