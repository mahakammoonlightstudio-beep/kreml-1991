# Patch pass 6: cross marks re-swapped (patch5 rebuild reintroduced U+2716),
# vodka well slimmed to 10 rows (drop the two middle option blurbs, keep Pravda's).
import sys
sys.stdout.reconfigure(encoding='utf-8')

def read(name):
    return open(name, encoding='utf-8').read().split('\n')
flash = read('.hallmark/flash.txt')
src = open('.hallmark/build_panels.py', encoding='utf-8').read()
ns = {'read': read, 'flash': flash}
exec(src[:src.index("panels = {}")], ns)
row, block = ns['row'], ns['block']

new_vodka = block([
    (146, 'dim'), (147, 'plain'), (148, 'plain'), (149, 'dim'),
    (150, 'plain'), (152, 'plain'), (154, 'plain'),
    (156, 'mark'), (157, 'plain'),
], flash)

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()
n = t.count('<span class="dim">✖</span>')
t = t.replace('<span class="dim">✖</span>', '<span class="dim">×</span>')
print('cross marks swapped:', n)

i = t.index('aria-label="A flash crisis printed')
a = t.index('<pre aria-hidden="true">', i)
b = t.index('</pre>', a) + len('</pre>')
t = t[:a] + '<pre aria-hidden="true">' + '\n'.join(new_vodka) + '</pre>' + t[b:]

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('patched; size', len(t))
