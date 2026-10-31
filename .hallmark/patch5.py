# Patch pass 5: rebuild the dossier well with correct line numbers
# (box 49/50/51, TIMELINE 52, roads head 66, pipeline 67, available purge 75, treaty 77).
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
    (67, 'lock'), (75, 'mark'), (77, 'lock'),
], dossier)

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()
i = t.index('aria-label="The dossier listing')
a = t.index('<pre aria-hidden="true">', i)
b = t.index('</pre>', a) + len('</pre>')
t = t[:a] + '<pre aria-hidden="true">' + '\n'.join(new_dossier) + '</pre>' + t[b:]
open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('dossier rebuilt; size', len(t))
