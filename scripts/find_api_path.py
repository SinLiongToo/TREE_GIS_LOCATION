with open('scripts/inspect_oldtree_api.py', 'r') as f:
    pass

import urllib.request, ssl
ctx = ssl._create_unverified_context()
url = 'https://map.oldtree.life/static/js/main.8f006f5e.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, context=ctx)
content = resp.read().decode('utf-8', errors='ignore')

idx = 0
while True:
    pos = content.find('map.oldtree.life/api', idx)
    if pos == -1:
        break
    start = max(0, pos - 100)
    end = min(len(content), pos + 200)
    print("--- SNIPPET ---")
    print(content[start:end])
    idx = pos + 1
