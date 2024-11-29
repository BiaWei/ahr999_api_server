# AHR999 API Server

[English Version](https://github.com/BiaWei/ahr999_api_server/blob/main/README.md) | [简体中文](https://github.com/BiaWei/ahr999_api_server/blob/main/README.zh.md)

### ahr999_api_server Documentation

---

## 1. Project Overview

`ahr999_api_server` is a Python-based cryptocurrency price monitoring and analysis tool designed to help users track cryptocurrency price changes. It calculates the AHR999 index based on specific algorithms, providing valuable insights for decision-making.

The **Bitcoin AHR999 Hoarding Index** is an index created by Weibo user `ahr999` to assist Bitcoin fixed investment users in making investment decisions with timing strategies. This index combines the short-term fixed investment yield of Bitcoin with the degree of deviation of Bitcoin price from expected valuation, offering more comprehensive market information.

The calculation method is:

$$
ahr999 = \frac{\text{spot price}}{\text{200-day geometric price}} \times \frac{\text{spot price}}{\text{predicted price}}
$$

Where:
- **spot price**: The current Bitcoin price.
- **200-day geometric price**: The average fixed investment cost (geometric mean) over the past 200 days.
- **predicted price**: The exponential prediction valuation, which is a linear regression fit of the coin age (days since 2009/1/3) and the logarithm of historical prices, calculated based on the coin age of the day.

### AHR999 Index Ranges:
- **ahr999 < 0.45**: Bottom-hunting range (e.g., appeared in 2022/6, 2022/9, 2022/11, and 2023/9).
- **0.45 < ahr999 < 1.2**: Fixed investment range.
- **ahr999 > 1.2**: Stop fixed investment and sell, based on other indicators.

---

## 2. Features

- **Real-time Price Monitoring**: Automatically fetches BTC-USDT price data from OKX every minute and records it.
- **AHR999 Index Calculation**: Computes the AHR999 index using the latest price, 200-day average investment cost, and exponential growth model.
- **Subscription Feature**: Allows users to subscribe to the current AHR999 index and receive notifications about price changes via the Bark app on iPhone.

---

## 3. Functional Modules

### `main.py`
- The main server script. Fetches the AHR999 index every minute and determines whether to send push notifications.

### `start.py`
- Sets up and starts the server using `uvicorn`.

### `globals.py`
- Defines global variables and the `Subscription` class.
    - **subscriptions**: Temporarily store subscription information.
    - **full_data**: Full data object including AHR999 index value, last update time, latest price, 200-day average cost, and exponential growth valuation.
    - **Subscription class**: Defines subscription-related information.

### `subscription.py`
- Loads and saves subscription information.
    - `load_subscriptions()`: Loads subscription data into global variables.
    - `save_subscriptions()`: Saves subscription data into a local JSON file.

### `server.py`
- Defines API endpoints.
    - `decode_base64_url(encoded_url: str)`: Decodes a base64-encoded Bark URL.
    - `send_token(encoded_url: str)`: Sends the current AHR999 index to the provided Bark URL.
    - `get_full_data()`: Returns the full data JSON object.
    - `bark_subscribe(encoded_url: str)`: POST request to subscribe, takes URL, notification settings, and price change threshold.
    - `bark_unsubscribe(encoded_url: str)`: POST request to unsubscribe.
    - `get_subscribe_data()`: GET request to return all subscription information.
    - `cal_price(ahr999: float)`: Estimates price based on given AHR999, growth evaluation, and past 200 days' average investment cost.
    - `cal_ahr999(price: float)`: Estimates AHR999 based on the given price.

### `ahr999.py`
- Handles AHR999 index calculations.
    - `cal_ahr999()`: Calculates the AHR999 index.
    - `predict_price()`: Predicts prices based on the coin's age and historical prices.

### `price.py`
- Fetches the BTC-USDT price from OKX.
    - `get_btc_price()`: Fetches the current BTC-USDT price.

### `savedata.py`
- Saves price information to CSV files using pandas.
    - `write_daily_file()`: Writes daily price and AHR999 data.
    - `write_overall_file()`: Writes overall data including date, price, geometric mean, and predicted price.

### `test/url_test.py`
- Contains optional test cases for five API endpoints, which can be run independently.

---

## 4. File Structure


```
test/: Test files.

data/: Directory for storing subscription information(subscriptions.json), daily prices (price at 00:00)(price.csv), and per-minute prices for a single day (historical/yyyy-mm-dd.csv).

html/: Frontend HTML files served by FastAPI.

legacy(useless)/: Deprecated files.
```

---

## 5. Usage Instructions

### Install Dependencies


```
pip install -r requirements.txt
```


### Configuration

1. Modify the server URL in `html/index.html` to set the server address.
2. Update `server_url` in `test/url_test.py` for testing.
3. Set `bark_url` in `test/url_test.py` to your Bark URL for testing.
4. Adjust the URLs in `MESSAGE_TEMPLATE` in `notification.py` to point to the server address. Clicking on the Bark notification on your iPhone will redirect to the frontend HTML.
5. When cloning this repository, use `sync.py` to download historical price data, as the repo does not contain the necessary price data to calculate the 200-day average cost.

### Start the Server

```
python start.py
```


### API Endpoints

- **Get Full Data**: `/get_full_data` (GET)
- **Fetch Data and Send via Bark**: `/send_token` (GET)
- **Subscribe**: `/bark_subscribe` (POST)
- **Unsubscribe**: `/bark_unsubscribe` (POST)
- **Get All Subscription Data**: `/get_subscribe_data` (GET)
