# Patch pass 8: shave the y=2700 word window under 80.
# 1) dossier well rebuilt without the Renewed Union Treaty row (7 words)
# 2) medium deal cell loses "Three reserves." (2 words)
# 3) U+2716 re-swapped for the multiplication sign after any rebuild
import sys
sys.stdout.reconfigure(encoding='utf-8')

def read(name):
    return open(name, encoding='utf-8').read().split('\n')
dossier = read('.hallmark/dossier.txt')
src = open('.hallmark/build_panels.py', encoding='utf-8').read()
ns = {'read': read, 'dossier': dossier}
exec(src[:src.index("panels = {}")], ns)
row, block = ns['row'], ns['block']

new_dossier = block([
    (49, 'dim'), (50, 'dim'), (51, 'dim'), (52, 'plain'), (66, 'dim'),
    (67, 'lock'), (75, 'mark'),
], dossier)

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()

i = t.index('aria-label="The dossier listing')
a = t.index('<pre aria-hidden="true">', i)
b = t.index('</pre>', a) + len('</pre>')
t = t[:a] + '<pre aria-hidden="true">' + '\n'.join(new_dossier) + '</pre>' + t[b:]

n = t.count('<span class="dim">✖</span>')
t = t.replace('<span class="dim">✖</span>', '<span class="dim">×</span>')
print('cross marks swapped:', n)

before = '<td>The historical grind. Three reserves.</td>'
after = '<td>The historical grind.</td>'
assert before in t
t = t.replace(before, after, 1)

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('patched; size', len(t))
