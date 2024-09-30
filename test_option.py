import requests
import datetime

# API endpoint
url = "https://www.okx.com/api/v5/public/mark-price"

# Parameters
params = {
    "instType": "OPTION",  # Replace with the desired product type
    "uly": "",  # Optional: Replace with the desired underlying index
    "instFamily": "",  # Optional: Replace with the desired instrument family
    "instId": "BTC-USD-240719-70000-C"  # Optional: Replace with the desired instrument ID
}

# Send GET request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Check if 'data' key exists and is not empty
    if 'data' in data and len(data['data']) > 0:
        # Extract markPx and ts from the first element in 'data'
        mark_px = data['data'][0].get('markPx')
        ts_str = data['data'][0].get('ts')

        if ts_str is not None:
            # Convert ts from string to int
            ts_int = int(ts_str)

            # Convert UNIX timestamp to normal time
            normal_time = datetime.datetime.fromtimestamp(ts_int / 1000.0)

            # Print the results
            print(f"Mark Price: {mark_px}")
            print(f"Timestamp: {normal_time}")
        else:
            print("Timestamp (ts) is not available in the response.")
    else:
        print("Data is not available in the response.")
else:
    # Print the error code and message
    print(f"Error {response.status_code}: {response.text}")
