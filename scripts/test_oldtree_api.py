import urllib.request
import ssl
import json

ctx = ssl._create_unverified_context()
url = 'https://map.oldtree.life/api/Tree/trees'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('Type:', type(data))
        if isinstance(data, list):
            print('Count:', len(data))
            if len(data) > 0:
                print('Sample 0:', json.dumps(data[0], ensure_ascii=False, indent=2))
        elif isinstance(data, dict):
            print('Keys:', list(data.keys()))
            for k, v in data.items():
                if isinstance(v, list):
                    print(f'Key {k} has {len(v)} items. First item:', v[0] if v else 'empty')
except Exception as e:
    print('Error:', e)
