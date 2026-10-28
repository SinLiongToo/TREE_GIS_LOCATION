import urllib.request
import ssl
import json
import re

ctx = ssl._create_unverified_context()
url = 'https://map.oldtree.life/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print('Length:', len(html))
        # Look for script sources or api urls
        for s in re.findall(r'src=[\'"]([^\'"]+)[\'"]', html):
            print('Script:', s)
        for u in re.findall(r'https?://[^\s"\'<>]+', html):
            if any(k in u.lower() for k in ['api', 'json', 'data', 'geojson', 'tree']):
                print('Found URL:', u)
except Exception as e:
    print('Error:', e)
