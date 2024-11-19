import base64
import requests
import time

# your server url
server_url = "http://127.0.0.1:11452/"

# your bark url here
bark_url = "https://api.day.app/XXXXXXXXXXXXXX/"
encoded_url = base64.urlsafe_b64encode(bark_url.encode('utf-8')).decode('utf-8')
print(f"encoded url: {encoded_url}")


# GET 请求
def get_request(rq_url, params=None):
    try:
        response = requests.get(rq_url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 假设返回的是 JSON 数据
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# POST 请求
def post_request(url, data=None, json=None, params=None):
    try:
        response = requests.post(url, data=data, json=json, params=params)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 假设返回的是 JSON 数据
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


# test
if __name__ == "__main__":

    # /send_token
    get_url = f"{server_url}send_token"
    get_params = {"encoded_url": encoded_url}
    get_response = get_request(get_url, get_params)
    print("send_token result:", get_response)

    # /get_full_datac
    get_url = f"{server_url}get_full_data"
    get_response = get_request(get_url)
    print("get_full_data result:", get_response)

    # bark_subscribe
    post_url = f"{server_url}bark_subscribe"
    enable_notification = True
    quote_threshold_value = 0.01
    query_params = {
        "encoded_url": encoded_url,
        "enable_quote_notif": True,
        "quote_threshold": quote_threshold_value
    }
    # send POST
    post_response = post_request(post_url, params=query_params)
    print("Subscribe result:", post_response)

    time.sleep(1)

    # bark_unsubscribe
    query_params = {
        "encoded_url": encoded_url,
    }
    post_url = f"{server_url}bark_unsubscribe"
    post_response = post_request(post_url, params=query_params)
    print("Subscribe result:", post_response)

    time.sleep(1)

    # /get_subscribe_data
    get_url = f"{server_url}get_subscribe_data"
    get_response = get_request(get_url)
    print("get_subscribe_data result:", get_response)



