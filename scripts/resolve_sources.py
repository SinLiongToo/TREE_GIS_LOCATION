import urllib.request
import ssl
import re

ctx = ssl._create_unverified_context()

def check_url(name, url):
    print(f"=== {name} ===")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            target = resp.geturl()
            print('Target:', target)
            html = resp.read().decode('utf-8', errors='ignore')
            for l in re.findall(r'https?://[^\s"\'<>]+', html):
                if any(k in l.lower() for k in ['csv', 'download', 'resource', 'dataset', 'kcg', 'xlsx', 'json', 'pdf']):
                    print('Found link:', l)
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    check_url('Kaohsiung ODPortal', 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYfM80_xaAUm__WAjGoQVLrJ1auBrFoF7XG8cPC8zc-4kU1wtFnSn2QTrCe3Els6AIqpHmwfjjla2_zZJ_Jr0UAWCqCyRvMt_WwjYS3RtUzZHs7M4A8SQ5oSs=')
