import requests
import os

url = 'https://www.agriculture.taichung.gov.tw/media/1474860/%E8%87%BA%E4%B8%AD%E5%B8%82%E5%8F%97%E4%BF%9D%E8%AD%B7%E6%A8%B9%E6%9C%A8%E7%B8%BD%E5%85%AC%E5%91%8A%E6%B8%85%E5%86%8A-1150903%E6%9B%B4%E6%96%B0-1.pdf'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.agriculture.taichung.gov.tw/12889/13054/13102/13117/312623'
}

r = requests.get(url, headers=headers, verify=False, timeout=15)
print('Status:', r.status_code, 'Content-Type:', r.headers.get('Content-Type'), 'Size:', len(r.content))
if r.status_code == 200:
    with open('data/raw/taichung_protected_trees_official.pdf', 'wb') as f:
        f.write(r.content)
    print('Successfully saved Taichung PDF!')
else:
    print('Failed:', r.status_code)
