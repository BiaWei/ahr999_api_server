from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import requests
import globals
import subscribe
import base64
from ahr999 import cal_ahr999
from urllib.parse import quote
from fetch_24h_price import fetch_24h_high_low

router = APIRouter()

def decode_base64_url(encoded_url: str) -> str:
    """解码 base64 编码的 URL"""
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_url.encode('utf-8'))
        decoded_url = decoded_bytes.decode('utf-8')
        return decoded_url
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 encoded URL: {str(e)}")

@router.get("/send_token")
def send_token(encoded_url: str):
    bark_send_url = decode_base64_url(encoded_url)
    url = f"{bark_send_url}{quote(globals.url_data['title'])}/{quote(globals.url_data['text'])}?icon={globals.url_data['icon']}&group=ahr999Server"
    print(f"url: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return {"message": "Request to external API successful", "status_code": response.status_code}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to reach external API")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_full_data")
def get_full_data():
    return globals.full_data


@router.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("html/index.html")


@router.get("/get_high_low")
def get_high_low():
    # 获取最近24h内的最高值和最低值
    high_24h, low_24h = fetch_24h_high_low()

    # 取现货价格算振幅
    spot_price = float(globals.full_data["price"])
    price_amplitude = round((high_24h - low_24h) / spot_price * 100, 3)

    # 算最高点和最低点往上/往下5%和8%的值
    amplitude_plus_5per = round(high_24h * 1.05, 1)
    amplitude_plus_8per = round(high_24h * 1.08, 1)
    amplitude_minus_5per = round(low_24h * 0.95, 1)
    amplitude_minus_8per = round(low_24h * 0.92, 1)

    price_high_low = {
        "high_24h": round(high_24h, 2),
        "low_24h": round(low_24h, 2),
        "price_amplitude": price_amplitude,
        "price": round(spot_price, 2),
        "amplitude_plus_5per": amplitude_plus_5per,
        "amplitude_plus_8per": amplitude_plus_8per,
        "amplitude_minus_5per": amplitude_minus_5per,
        "amplitude_minus_8per": amplitude_minus_8per
    }
    return price_high_low

@router.post("/bark_subscribe")
def bark_subscribe(encoded_url: str, enable_quote_notif: bool = Query(...), quote_threshold: float = Query(...)):
    new_subscribe_url = decode_base64_url(encoded_url)
    subscription_exists = False

    for sub in globals.subscriptions:
        if sub.url == new_subscribe_url:
            # 更新现有订阅的参数
            sub.enable_quote_notif = enable_quote_notif
            sub.quote_threshold = quote_threshold
            subscription_exists = True
            break

    if not subscription_exists:
        # 添加新的订阅
        subscription = globals.Subscription(new_subscribe_url, enable_quote_notif, quote_threshold)
        globals.subscriptions.append(subscription)

    # 试着访问一下订阅url 如返回200则加入订阅
    try:
        response = requests.get(f"{new_subscribe_url}{quote('Successfully subscribe!')}/url:{quote(new_subscribe_url, safe='')}?icon={globals.url_data['icon']}&group=ahr999Server")
        if response.status_code == 200:
            subscribe.save_subscriptions()
            return {"message": "Request to external API successful", "status_code": response.status_code}

        else:
            print(f"failed to subscribe! URL: {new_subscribe_url}, Code: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Failed to subscribe!")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bark_unsubscribe")
def bark_unsubscribe(encoded_url: str):
    url = decode_base64_url(encoded_url)
    for sub in globals.subscriptions:
        if sub.url == url:
            globals.subscriptions.remove(sub)
            subscribe.save_subscriptions()
            try:
                requests.get(f"{url}{quote('Successfully unsubscribe!')}/url:{quote(url, safe='')}?icon={globals.url_data['icon']}&group=ahr999Server")
            except requests.exceptions.RequestException as e:
                print("Successfully unsubscribe, but failed to send notification")
                raise HTTPException(status_code=500, detail=str(e))
            return {"message": "Unsubscribed successfully", "url": url}
    raise HTTPException(status_code=404, detail="URL not found in subscriptions")

@router.get("/get_subscribe_data")
def get_subscribe_data():
    return globals.subscriptions

@router.get("/cal_ahr999")
def echo_float(price: float):
    ahr999 = cal_ahr999(price, globals.full_data["cost_200day"], globals.full_data["exp_growth_valuation"])
    return {"ahr999": ahr999}

@router.get("/cal_price")
def echo_float(ahr999: float):
    price_get = (ahr999 * globals.full_data["cost_200day"] * globals.full_data["exp_growth_valuation"]) ** 0.5
    return {"price": price_get}
