import okx.MarketData as MarketData
import time


# Get price from okx
def get_btc_price(inst_id, retries=5, delay=5):
    # Product trading: 0, demo trading: 1
    flag = "0"

    for attempt in range(retries):
        try:
            # Get latest BTC price
            market_data_api = MarketData.MarketAPI(flag=flag)
            price_json = market_data_api.get_ticker(instId=inst_id)
            latest_btc_price = price_json['data'][0]['last']
            return latest_btc_price
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retry attempts failed.")
                return None


