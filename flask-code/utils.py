# utils.py
import requests
from datetime import datetime, timedelta

exchange_rate_cache = {
    "rate": None,
    "last_updated": None
}

def get_usd_to_cny_rate():
    now = datetime.now()
    if exchange_rate_cache["rate"] and exchange_rate_cache["last_updated"]:
        if now - exchange_rate_cache["last_updated"] < timedelta(minutes=10):
            return exchange_rate_cache["rate"]
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        usd_to_cny = data["rates"]["CNY"]
        exchange_rate_cache["rate"] = usd_to_cny
        exchange_rate_cache["last_updated"] = now
        return usd_to_cny
    except Exception as e:
        print(f"获取汇率失败: {e}")
        return None
