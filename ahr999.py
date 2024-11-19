import pandas as pd
import numpy as np


def cal_ahr999(current_price, geometric_mean_last_200, predicted_price):
    # ensure geometric_mean_last_200 and predicted_price are float
    geometric_mean_last_200 = float(geometric_mean_last_200)
    predicted_price = float(predicted_price)
    current_price = float(current_price)

    # calculate ahr999 index
    ahr999 = (current_price / predicted_price) * (current_price / geometric_mean_last_200)
    return ahr999


def predict_price(base_date, get_date):
    # calculate age of bitcoin from base_date to now (get_gate)
    coin_age_days = (pd.to_datetime(get_date) - pd.to_datetime(base_date)).days

    # use fixed fitting parameters to calculate predicted price
    predicted_price = 10 ** (5.84 * np.log10(coin_age_days) - 17.01)

    return predicted_price


