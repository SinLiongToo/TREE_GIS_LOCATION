import re

with open('scripts/inspect_oldtree_js.py', 'r') as f:
    pass

import urllib.request, ssl
ctx = ssl._create_unverified_context()
url = 'https://map.oldtree.life/static/js/main.8f006f5e.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, context=ctx)
content = resp.read().decode('utf-8', errors='ignore')

# Search for any string mentioning "api/" or "/trees" or similar
matches = re.findall(r'[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]', content)
for m in set(matches):
    print('Match:', m)

# Search for axios/fetch calls
fetches = re.findall(r'(?:get|post|fetch)\([\'"`]([^\'"`]+)[\'"`]', content)
for f in set(fetches):
    print('Fetch:', f)
