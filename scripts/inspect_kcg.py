import urllib.request
import ssl
import re

ctx = ssl._create_unverified_context()
url = 'https://data.kcg.gov.tw/dataset/commemoration-tree'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print('KCG page length:', len(html))
        for l in re.findall(r'href=[\'"]([^\'"]+)[\'"]', html):
            if any(k in l.lower() for k in ['csv', 'download', 'resource']):
                print('KCG link:', l)
except Exception as e:
    print('KCG error:', e)
