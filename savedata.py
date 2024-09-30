import os
import pandas as pd


def write_file_3col(file_path, date, price, ahr999):
    data = pd.DataFrame({
        'Date': [date],
        'Price': [price],
        'AHR999': [ahr999]
    })
    file_exists = os.path.exists(file_path)
    file_empty = os.path.getsize(file_path) == 0 if file_exists else True

    # 写入CSV文件
    if not file_exists or file_empty:
        # 文件不存在或为空，创建文件并写入数据和索引
        data.to_csv(file_path, index=False)
    else:
        # 文件存在且不为空，追加写入数据，不包含索引和表头
        data.to_csv(file_path, index=False, mode='a', header=False)


def write_file_4col(file_path, date, price, geometric_mean_price, predicted_price):
    data = pd.DataFrame({
        'Date': [date],
        'Price': [price],
        'Geometric Mean Price': [geometric_mean_price],
        'Predicted Price': [predicted_price]
    })
    file_exists = os.path.exists(file_path)
    file_empty = os.path.getsize(file_path) == 0 if file_exists else True

    if not file_exists or file_empty:
        # 文件不存在或为空，创建文件并写入数据和索引
        data.to_csv(file_path, index=False)
    else:
        # 文件存在，读取现有数据
        existing_data = pd.read_csv(file_path)

        if existing_data.empty:
            # 文件内容为空，直接写入
            data.to_csv(file_path, index=False)
        else:
            # 确保数据类型匹配
            data['Price'] = data['Price'].astype(existing_data['Price'].dtype)
            data['Geometric Mean Price'] = data['Geometric Mean Price'].astype(
                existing_data['Geometric Mean Price'].dtype)
            data['Predicted Price'] = data['Predicted Price'].astype(existing_data['Predicted Price'].dtype)

            # 检查最后一行的日期
            last_date = existing_data.iloc[-1]['Date']
            if last_date == date:
                # 日期相同，更新最后一行
                for column in data.columns:
                    existing_data.at[existing_data.index[-1], column] = data.at[0, column]
                existing_data.to_csv(file_path, index=False)
            else:
                # 日期不同，追加新行
                data.to_csv(file_path, index=False, mode='a', header=False)
