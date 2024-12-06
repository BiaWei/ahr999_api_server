from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import FileResponse
import os
import globals
import subscribe
import base64
import logging
import sys
import notification
from ahr999 import cal_ahr999

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 项目根目录
OVERALL_PRICE_PATH = os.path.join(BASE_DIR, "data", "price.csv")
ICON_PATH = os.path.join(BASE_DIR, "html", "favicon.ico")

router = APIRouter()


def decode_base64_url(encoded_url: str) -> str:
    """decode bark url encoded by base64"""
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_url.encode('utf-8'))
        decoded_url = decoded_bytes.decode('utf-8')
        return decoded_url
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 encoded URL: {str(e)}")


@router.get("/send_token")
def send_token(encoded_url: str):
    try:
        bark_send_url = decode_base64_url(encoded_url)
    except Exception as e:
        logger.error(f"Failed to decode URL: {e}")
        raise HTTPException(status_code=400, detail="Invalid encoded URL")

    try:
        notification.return_single_data(globals.full_data["ahr999"], globals.full_data["update_time"], bark_send_url)
        return {"message": "Notification sent successfully", "status_code": 200}
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=f"Notification sending failed: {str(e)}")


@router.get("/get_full_data")
def get_full_data():
    return globals.full_data


@router.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("html/index.html")

@router.get("/subscribe", response_class=FileResponse)
async def read_subscribe_page():
    return FileResponse("html/subscribe.html")


@router.post("/bark_subscribe")
def bark_subscribe(encoded_url: str = Form(...),
                   enable_quote_notif: bool = Form(...),
                   quote_threshold: float = Form(...)):

    new_subscribe_url = decode_base64_url(encoded_url)
    subscription_exists = False

    # if new url exists in subscriptions
    for sub in globals.subscriptions:
        if sub.url == new_subscribe_url:

            # update parameter of url
            sub.enable_quote_notif = enable_quote_notif
            sub.quote_threshold = quote_threshold
            subscription_exists = True
            break

    # bark url not exists
    if not subscription_exists:
        # add new subscriptions
        subscription = globals.Subscription(new_subscribe_url, enable_quote_notif, quote_threshold)
        globals.subscriptions.append(subscription)

    # Try GET bark url, save subscriptions if got 200.
    try:
        notification.send_subscribe_notification(new_subscribe_url)
        subscribe.save_subscriptions()
        return {"message": "Subscribe successfully", "status_code": 200}

    except ValueError as e:
        logger.warning(f"Subscription failed, URL not found: {new_subscribe_url}, error: {e}")
        raise HTTPException(status_code=404, detail="Subscription URL not found.")

    except Exception as e:
        logger.error(f"Failed to subscribe, URL: {new_subscribe_url}, error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bark_unsubscribe")
def bark_unsubscribe(encoded_url: str = Form(...)):
    url = decode_base64_url(encoded_url)
    for sub in globals.subscriptions:
        if sub.url == url:
            globals.subscriptions.remove(sub)
            subscribe.save_subscriptions()
            try:
                notification.send_unsubscribe_notification(url)
                return {"message": "Unsubscribe successful", "status_code": 200}

            except Exception as e:
                logger.error(f"Unsubscribe success, but failed to send notification! URL: {url}, error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    raise HTTPException(status_code=404, detail="URL not found in subscriptions")



@router.post("/bark_query")
def bark_query(encoded_url: str = Form(...)):
    url = decode_base64_url(encoded_url)
    for sub in globals.subscriptions:
        if sub.url == url:
            return {"data": sub.to_dict(), "status_code": 200}

    raise HTTPException(status_code=404, detail="URL not found in subscriptions")


# Get all subscribed bark url
# You can delete this from being leaked
# @router.get("/get_subscribe_data")
# def get_subscribe_data():
#     return globals.subscriptions


@router.get("/download/history_price", response_description="Download a fixed file")
async def download_file():
    """
    提供固定文件的下载
    """
    if not os.path.exists(OVERALL_PRICE_PATH):
        return {"error": "File not found"}  # 如果文件不存在，返回错误信息

    # 返回文件响应
    return FileResponse(OVERALL_PRICE_PATH, filename="price.csv", media_type="application/octet-stream")


@router.get("/favicon.ico")
async def get_favicon():
    return FileResponse(ICON_PATH, media_type="image/x-icon")

# calculate ahr999 from input bitcoin price
@router.get("/cal_ahr999")
def echo_float(price: float):
    ahr999 = cal_ahr999(price, globals.full_data["cost_200day"], globals.full_data["exp_growth_valuation"])
    return {"ahr999": ahr999}


# calculate bitcoin price from ahr999 today
@router.get("/cal_price")
def echo_float(ahr999: float):
    price_get = (ahr999 * globals.full_data["cost_200day"] * globals.full_data["exp_growth_valuation"]) ** 0.5
    return {"price": price_get}
