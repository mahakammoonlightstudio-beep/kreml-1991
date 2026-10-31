import re

h = open('docs/index.html', encoding='utf-8').read()
m = re.search(r'<pre aria-hidden="true">(.*?)</pre>', h, re.S)
txt = re.sub(r'<[^>]+>', '', m.group(1))
lines = [l.rstrip() for l in txt.split('\n')]
for n, l in enumerate(lines):
    if not l:
        continue
    runs, prev = [], None
    for k, ch in enumerate(l, 1):
        cls = ('space' if ch == ' ' else 'cell' if ch in '█▏░▎▍▋▊━…' else
               'word' if (ch.isalnum() or ch in '☭$&') else 'punct')
        if cls != prev:
            runs.append([cls, k, k])
        else:
            runs[-1][2] = k
        prev = cls
    print(n, len(l), runs[:16])
