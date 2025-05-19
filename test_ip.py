import requests

proxy = "socks5h://51.68.175.56:1080"

session = requests.Session()
session.proxies = {
    "http": proxy,
    "https": proxy
}

try:
    res = session.get("https://api.ipify.org?format=json", timeout=5)
    print("代理 IP:", res.json())
except Exception as e:
    print(f"代理連線失敗: {e}")
