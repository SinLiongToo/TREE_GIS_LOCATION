import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.agriculture.taichung.gov.tw/12889/13054/13102/13117/312623'
r = requests.get(url, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.find_all('a'):
    t = a.text.strip()
    if '總公告' in t or '清冊' in t or '受保護' in t:
        print('A tag:', t, a.attrs)
