import urllib.request
import ssl
import re

ctx = ssl._create_unverified_context()
r_url = 'https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFM8Srn1escf-NfjXVxf2o4dQf2hT7-QoYzzu-YpnmOWljz6kywn9682xWH-Ba6HyZskD--Syqe0rZUllGWYBDeda233mrmyu_yKXy31P3Fo-8UbyN8uH2XhAvwUN1hb95__QpAArQewzwIphaPTojHPWTqv29T83ylPrvegUmotCSQb0SvzFt9JsJ5Pf9y1aanKAhogY0WP80tocR1FdeHsUKi-tVE26TIRZYUCBexj4HEKZTddOj7USKiGQdZJiuGUvJoKkEBQ2B3oe-E7UbowZ3sbuhrr8FBiX9JxM9DjW9giP0oZYN1dTRFvOBVDiTgt2x4Uw4Ifo8oDsqpSnGX9DjVIsDN2JyyWYA='
req = urllib.request.Request(r_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        print('Target:', resp.geturl())
        content = resp.read()
        print('Length:', len(content), 'Content-Type:', resp.headers.get('Content-Type'))
        if b'%PDF' in content[:20]:
            print('Is valid PDF!')
            with open('data/raw/hualien_protected_trees.pdf', 'wb') as f:
                f.write(content)
            print('Saved to data/raw/hualien_protected_trees.pdf')
except Exception as e:
    print('Error:', e)
