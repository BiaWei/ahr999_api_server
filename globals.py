# globals.py

class Subscription:
    def __init__(self, url, enable_quote_notif, quote_threshold, last_send_price=None):
        if last_send_price is None:
            last_send_price = []
        self.url = url
        self.enable_quote_notif = enable_quote_notif
        self.quote_threshold = quote_threshold
        self.last_send_price = last_send_price

    def to_dict(self):
        return {
            "url": self.url,
            "enable_quote_notif": self.enable_quote_notif,
            "quote_threshold": self.quote_threshold
        }


full_data = {
    "ahr999": "",
    "update_time": "",
    "unix_time": "",
    "price": "",
    "cost_200day": "",
    "exp_growth_valuation": ""
}

subscriptions = []
