import re
import requests

# 取得免費代理 IP 列表
res = requests.get('https://free-proxy-list.net/')
free_ips = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', res.text)

valid_ips = []

# 測試哪些代理可以用
for ip in free_ips:
    try:
        proxies = {'http': f'http://{ip}', 'https': f'http://{ip}'}
        res = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=5)
        
        if res.status_code == 200:
            ip_address, port = ip.split(':')
            valid_ips.append({'ip': ip_address, 'port': port})
            print(f'✔ WORKING: {ip}')
    except Exception as e:
        print(f'❌ FAIL: {ip} - {e}')

print(f"✅ 可用的代理 IP：{valid_ips}")
