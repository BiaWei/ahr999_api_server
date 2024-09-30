import pandas as pd
import numpy as np


def cal_ahr999(current_price, geometric_mean_last_200, predicted_price):
    # 确保geometric_mean_last_200和predicted_price是浮点数
    geometric_mean_last_200 = float(geometric_mean_last_200)
    predicted_price = float(predicted_price)
    current_price = float(current_price)

    # 计算AHR999指数
    ahr999 = (current_price / predicted_price) * (current_price / geometric_mean_last_200)
    return ahr999


def predict_price(base_date, get_date):
    # 计算币龄
    coin_age_days = (pd.to_datetime(get_date) - pd.to_datetime(base_date)).days
    # 使用固定参数计算指数增长估值
    predicted_price = 10 ** (5.84 * np.log10(coin_age_days) - 17.01)
    return predicted_price


