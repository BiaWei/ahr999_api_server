import pandas as pd
from datetime import datetime, timedelta


def fetch_24h_high_low():

    """
    get highest and lowest price in 24 hours
    """

    current_datetime = datetime.now()

    # or use the time you specify
    # current_datetime = datetime.strptime("2024-06-21 10:00", "%Y-%m-%d %H:%M")

    # define path and format
    file_path = "../data/historical"
    file_format = "*.csv"

    # get the same time of yesterday
    previous_datetime = current_datetime - timedelta(days=1)

    # read price file of today and yesterday
    current_file = f"{file_path}/{current_datetime.strftime('%Y-%m-%d')}.csv"
    previous_file = f"{file_path}/{previous_datetime.strftime('%Y-%m-%d')}.csv"

    # read files
    current_df = pd.read_csv(current_file, parse_dates=["Date"])
    previous_df = pd.read_csv(previous_file, parse_dates=["Date"])

    # filter data of yesterday
    previous_df = previous_df[previous_df["Date"] >= previous_datetime]

    # merge data
    combined_df = pd.concat([previous_df, current_df])

    # calculate max and min
    max_price = combined_df["Price"].max()
    min_price = combined_df["Price"].min()

    print(f"Max: {max_price}")
    print(f"Min: {min_price}")

    return max_price, min_price

# fetch_24h_high_low()