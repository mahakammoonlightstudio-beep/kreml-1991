import re
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
url = 'https://fonts.googleapis.com/css2?family=Martian+Mono:wdth,wght@75..112.5,400..700&display=block'
css = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode()

blocks = {}
for block in re.findall(r'/\*\s*(\S+)\s*\*/\s*(@font-face\s*\{[^}]+\})', css):
    subset, face = block
    blocks[subset] = face

keep = ['cyrillic-ext', 'cyrillic', 'latin-ext', 'latin', 'vietnamese']
out = []
out_dir = 'docs/assets/fonts'
import os
os.makedirs(out_dir, exist_ok=True)
for subset in keep:
    if subset not in blocks:
        continue
    face = blocks[subset]
    m = re.search(r'url\((https://[^)]+\.woff2)\)', face)
    link = m.group(1)
    name = f'martian-mono-{subset}.woff2'
    data = urllib.request.urlopen(urllib.request.Request(link, headers=UA), timeout=60).read()
    with open(os.path.join(out_dir, name), 'wb') as f:
        f.write(data)
    face = face.replace(link, f'fonts/{name}')
    face = re.sub(r'font-display:\s*\w+', 'font-display: block', face)
    out.append(f'/* {subset} */\n{face}')
    print(subset, len(data), 'bytes')

with open('.hallmark/fonts_local.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('kept subsets:', [s for s in keep if s in blocks])
