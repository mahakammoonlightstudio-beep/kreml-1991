# Patch pass 2 on docs/index.html:
# 1) slimmer directive menu (drop items 2 and 4) and dossier (drop PATH line, gold line)
# 2) table becomes a stacked ledger on phones
# 3) S3 lead dropped, deal copy tightened
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, '.hallmark')
def read(name):
    return open(name, encoding='utf-8').read().split('\n')
flash = read('.hallmark/flash.txt')
dossier = read('.hallmark/dossier.txt')

import importlib.util
spec = importlib.util.spec_from_file_location('bp', '.hallmark/build_panels_lib.py')

# reuse the row() and block() from build_panels by exec'ing its functions
src = open('.hallmark/build_panels.py', encoding='utf-8').read()
ns = {}
# keep only the helpers (drop main flow that writes files)
cut = src.index("panels = {}")
head = src[:cut]
ns = {'read': read, 'flash': flash, 'dossier': dossier}
exec(src[:src.index("panels = {}")], ns)
row, block = ns['row'], ns['block']

new_directive = block([
    (121, 'dim'), (122, 'val'), (123, 'plain'), (132, 'val'), (134, 'plain'),
    (142, 'mark'), (143, 'plain'), (144, 'mark'),
], flash)
new_dossier = block([
    (50, 'dim'), (51, 'dim'), (52, 'dim'), (53, 'plain'),
    (66, 'dim'), (67, 'lock'), (70, 'lock'), (75, 'mark'), (77, 'lock'),
], dossier)

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()

def swap(fig_label_frag, new_rows):
    global t
    i = t.index(fig_label_frag)
    a = t.index('<pre aria-hidden="true">', i)
    b = t.index('</pre>', a) + len('</pre>')
    t = t[:a] + '<pre aria-hidden="true">' + '\n'.join(new_rows) + '</pre>' + t[b:]

swap('aria-label="The yearly directive menu', new_directive)
swap('aria-label="The dossier listing', new_dossier)

# --- copy trims ---
t = t.replace(' <p class="lead">Six presets own the drift and the reserves. Four scenarios own the first year.</p>\n', '')
t = t.replace('<tr><td class="flag">hypotenuse', 'ZZZ')  # safety no-op
t = t.replace('<tr><td class="flag">medium</td><td>BALANCED</td><td>The historical grind, three reserves.</td></tr>',
              '<tr><td class="flag">medium</td><td>BALANCED</td><td>The historical grind. Three reserves.</td></tr>')
t = t.replace('<tr><td class="flag">hard</td><td>OLD GUARD IRON GRASP</td><td>Two reserves, and the system fights back.</td></tr>',
              '<tr><td class="flag">hard</td><td>OLD GUARD IRON GRASP</td><td>Two reserves. The system fights back.</td></tr>')
t = t.replace('<tr><td class="flag">extreme</td><td>THE SYSTEM ITSELF</td><td>A single reserve. The Union is a rumour you must keep alive.</td></tr>',
              '<tr><td class="flag">extreme</td><td>THE SYSTEM ITSELF</td><td>A single reserve; the Union is a rumour.</td></tr>')
t = t.replace('<tr><td class="flag">flash</td><td>FLASH CRISIS</td><td>Nine seconds a decision, two reserves.</td></tr>',
              '<tr><td class="flag">flash</td><td>FLASH CRISIS</td><td>Nine seconds a decision.</td></tr>')
t = t.replace('<tr><td class="flag">historical</td><td>HISTORICAL RAILS</td><td>Real decline only. Divergence costs score.</td></tr>',
              '<tr><td class="flag">historical</td><td>HISTORICAL RAILS</td><td>Real decline. Divergence costs score.</td></tr>')
t = t.replace('<tr><td class="flag">flashpoint</td><td>1980</td><td>The 40th Army in the mountains, twelve years left.</td></tr>',
              '<tr><td class="flag">flashpoint</td><td>1980</td><td>The 40th Army, twelve years left.</td></tr>')
t = t.replace('<p class="caption">About 12 MB on the first visit, then offline; the run survives a refresh.</p>',
              '<p class="caption">About 12 MB on the first visit, then offline.</p>')
t = t.replace('<p class="caption">Any gauge at zero ends the year. The portraits take the rest.</p>',
              '<p class="caption">Any gauge at zero ends the year.</p>')

# --- CSS: phone ledger tables; drop the side-by-side deals rule ---
t = t.replace('@media (min-width: 70rem) { .deals { grid-template-columns: 1fr 1fr; gap: var(--space-xl); } }\n', '')
css_add = '''@media (max-width: 40rem) {
  .deal table, .deal tbody { display: block; }
  .deal thead { display: none; }
  .deal tr { display: block; border-top: var(--rule-hair) solid var(--color-rule); padding-block: var(--space-sm); }
  .deal tr:first-child { border-top: 0; }
  .deal th, .deal td { display: block; padding: 0; border-top: 0; }
  .deal td.flag, .deal td:nth-child(2) { display: inline; padding-inline-end: var(--space-sm); }
}
'''
anchor = '.colophon .fine { margin-inline-start: auto; color: var(--color-muted); font-size: var(--text-sm); color: var(--color-muted); }\n'
assert anchor in t
t = t.replace(anchor, anchor + css_add, 1)

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('patched; size', len(t))
