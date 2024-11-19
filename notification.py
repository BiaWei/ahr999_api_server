from urllib.parse import quote
import requests
import logging
import sys
import time


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


MESSAGE_TEMPLATE = {
    "price_change": lambda price_change_str, price, ahr999: {
        "title": "Price change!",
        "body": f"Max price change {price_change_str}% in past 15 minutes, the current price is ${price}, ahr999 is {ahr999:.4f}.",
        "badge": 1,
        "sound": "",
        "icon": "https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png",
        "group": "ahr999Server",
        "url": "https://ahr999.3geeks.top"
    },
    "obtain_single_data": lambda ahr999, get_time: {
        "title": "Successfully obtain data!",
        "body": f"ahr999: {ahr999:.4f}\r\nLast update: {get_time.replace('/', '-')}",
        "badge": 1,
        "sound": "",
        "icon": "https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png",
        "group": "ahr999Server",
        "url": "https://ahr999.3geeks.top"
    },
    "new_subscribe": lambda new_subscribe_url: {
        "title": "Successfully subscribe!",
        "body": f"url:{new_subscribe_url}",
        "badge": 1,
        "sound": "",
        "icon": "https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png",
        "group": "ahr999Server",
        "url": "https://ahr999.3geeks.top"
    },
    "unsubscribe": lambda unsubscribe_url: {
        "title": "Successfully unsubscribe!",
        "body": f"url:{unsubscribe_url}",
        "badge": 1,
        "sound": "",
        "icon": "https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png",
        "group": "ahr999Server",
        "url": "https://ahr999.3geeks.top"
    },
}


def send_bark_notification(bark_url, payload, retries=3, retry_delay=2):
    """
    Sends a notification to the Bark server using the specified API key and payload.

    Args:
        bark_url (str): Your Bark url.
        payload (dict): The notification payload. Should include fields like "body", "title", etc.
        retries (int): Number of retries if the request fails. Default is 3.
        retry_delay (int): Delay between retries in seconds. Default is 2.

    Returns:
        dict: The response from the Bark server.
    """

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    for attempt in range(retries):
        try:
            logger.info(f"Sending notification to Bark server. Attempt {attempt + 1}...")
            response = requests.post(bark_url, json=payload, headers=headers)
            if response.status_code == 200:
                logger.info("Notification sent successfully.")
                return response.json()
            else:
                logger.warning(f"Attempt {attempt + 1} failed with status code {response.status_code}. Retrying...")
        except requests.RequestException as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")

        time.sleep(retry_delay)

    logger.critical("All retry attempts failed. Unable to send notification.")
    raise Exception("All retry attempts failed. Unable to send notification.")


def send_price_change_notification(price_change, latest_btc_price, ahr999, bark_url):
    """
    Sends price change notification.

    Args:
        price_change (float): Percentage of price change. For example:
            price_change = 1.5 will be converted to: "+1.5%"
            price_change = -2.0 will be converted to: "-2.0%"

        latest_btc_price (float): Latest BTC price.
        ahr999 (float): Ahr999 index.
        bark_url (str): Bark subscription URL of user.

    Returns:
        dict: The response from the Bark server.
    """

    change_sign = "+" if price_change > 0 else ""
    price_change_str = change_sign + f"{price_change:.2f}"

    try:
        result = send_bark_notification(
            bark_url,
            MESSAGE_TEMPLATE["price_change"](price_change_str, latest_btc_price, ahr999)
        )
        logger.info(f"Response from server: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise Exception("Failed to send notification.") from e


def return_single_data(ahr999, last_update_time, bark_url):
    """
    Sends data when user acquires ahr999

    Args:
        ahr999 (float): Ahr999 index.
        last_update_time: (str): Last update time.
        bark_url (str): Bark subscription URL of user.

    Returns:
        dict: The response from the Bark server.
    """

    try:
        result = send_bark_notification(
            bark_url,
            MESSAGE_TEMPLATE["obtain_single_data"](ahr999, last_update_time)
        )
        logger.info(f"Response from server: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise Exception("Failed to send notification.") from e



def send_subscribe_notification(bark_url):
    """
    Sends notification when user successfully subscirbe.

    Args:
        bark_url (str): Bark subscription URL of user.

    Returns:
        dict: The response from the Bark server.
    """

    try:
        result = send_bark_notification(
            bark_url,
            MESSAGE_TEMPLATE["new_subscribe"](bark_url)
        )
        logger.info(f"Response from server: {result}")
        return result
    except ValueError as e:
        logger.error(f"Failed to send notification: {e}")
        raise ValueError("Failed to send notification.") from e


def send_unsubscribe_notification(bark_url):
    """
    Sends notification when user successfully subscirbe.

    Args:
        bark_url (str): Bark subscription URL of user.

    Returns:
        dict: The response from the Bark server.
    """

    try:
        result = send_bark_notification(
            bark_url,
            MESSAGE_TEMPLATE["new_subscribe"](bark_url)
        )
        logger.info(f"Response from server: {result}")
        return result
    except ValueError as e:
        logger.error(f"Failed to send notification: {e}")
        raise ValueError("Failed to send notification.") from e

# test
if __name__ == "__main__":

    # your bark url
    bark_url = "https://api.day.app/XXXXXXXXXXXXXXXXX/"

    try:
        result = send_price_change_notification(-1.5, 90000, 1.4, bark_url)
        print(result)
    except Exception as e:
        print(f"Failed to send notification: {e}")

    try:
        result = return_single_data(1.4, "2024-11-19 17:12:26", bark_url)
        print(result)
    except Exception as e:
        print(f"Failed to send notification: {e}")

    try:
        result = send_subscribe_notification(bark_url)
        print(result)
    except Exception as e:
        print(f"Failed to send notification: {e}")

    try:
        result = send_subscribe_notification(bark_url)
        print(result)
    except Exception as e:
        print(f"Failed to send notification: {e}")

