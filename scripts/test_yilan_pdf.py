import urllib.request
import ssl

ctx = ssl._create_unverified_context()
r_url = 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY219itINRzOLuUPtqNbT8J237K7PVMQvX-Q4EMyti_Uhged92tZ4vqTBX4H6dHv4gLZumQIMTmwb2KAZYE6MQm8SU45zCHB7EpK4PDHfWO7RYC9codpmzDuCo0OAaqF1bFX5yGo_5mY9Ix8vOpEdf614n7iKVkK0VIAAybnuRAWkA_Jw9B730lLZLU6BTIE7C39g14kBTbbR4_BR2VCBVBIFtzeypMmtBWh8phNWQK6pfHs9UPQ635aG9XcTV1uvs5XgHplaKqN3qu-6ER-MIERP9gbag-on7B5msXrS0evNmdJIED-wqmBPSff7KImSUsTSSDw=='
req = urllib.request.Request(r_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        print('Target:', resp.geturl())
        content = resp.read()
        print('Length:', len(content), 'Content-Type:', resp.headers.get('Content-Type'))
        if b'%PDF' in content[:20]:
            print('Is valid PDF!')
            with open('data/raw/yilan_protected_trees.pdf', 'wb') as f:
                f.write(content)
            print('Saved to data/raw/yilan_protected_trees.pdf')
except Exception as e:
    print('Error:', e)
