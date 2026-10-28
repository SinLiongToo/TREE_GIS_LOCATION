import urllib.request
import ssl
import re

ctx = ssl._create_unverified_context()
url = 'https://map.oldtree.life/static/js/main.8f006f5e.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print('JS size:', len(content))
        # Find API endpoints
        endpoints = set(re.findall(r'https?://[^\s"\'`<>]+', content))
        for ep in endpoints:
            print('EP:', ep)
        # Find path patterns like "/api/..."
        paths = set(re.findall(r'[\'"`](/api/[^\'"`]+)[\'"`]', content))
        for p in paths:
            print('Path:', p)
except Exception as e:
    print('Error:', e)
