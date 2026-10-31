# Patch pass 4: leaner panels + tighter copy + wider inter-panel gap.
import sys
sys.stdout.reconfigure(encoding='utf-8')

def read(name):
    return open(name, encoding='utf-8').read().split('\n')
flash = read('.hallmark/flash.txt')
death = read('.hallmark/death.txt')

src = open('.hallmark/build_panels.py', encoding='utf-8').read()
ns = {'read': read, 'flash': flash, 'death': death}
exec(src[:src.index("panels = {}")], ns)
row, block = ns['row'], ns['block']

new_directive = block([
    (121, 'dim'), (132, 'val'), (134, 'plain'),
    (142, 'mark'), (143, 'plain'), (144, 'mark'),
], flash)
new_death = block([
    (1989, 'alarm'), (1990, 'plain'), (1991, 'dim'), (1994, 'plain'),
], death)

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()

def swap(fig_label_frag, new_rows):
    global t
    i = t.index(fig_label_frag)
    a = t.index('<pre aria-hidden="true">', i)
    b = t.index('</pre>', a) + len('</pre>')
    t = t[:a] + '<pre aria-hidden="true">' + '\n'.join(new_rows) + '</pre>' + t[b:]

swap('aria-label="The yearly directive menu', new_directive)
swap('aria-label="The collapse screen', new_death)

# copy trims (visible words)
t = t.replace('<p class="lead">Captured output of a BALANCED run. Colour is the only stage.</p>',
              '<p class="lead">Captured output of a BALANCED run.</p>')
t = t.replace('<p class="caption">One big public lever a year. You set it; the court grades it.</p>',
              '<p class="caption">One big public lever a year.</p>')
t = t.replace('<p class="caption">Under the v6 wall clock, nine seconds is the whole debate.</p>',
              '<p class="caption">Nine seconds is the whole debate.</p>')
t = t.replace('<p class="caption">Press d: the ledger of what you did, and the roads still shut.</p>',
              '<p class="caption">Press d: the roads still shut.</p>')
t = t.replace('<td>The treaty held. Ten years red.</td>', '<td>Treaty held. Ten years red.</td>')
t = t.replace('<td>The 40th Army, twelve years left.</td>', '<td>The 40th Army. Twelve years.</td>')
t = t.replace('<p class="caption">Python 3.8 or newer is the entire list. On Windows, <code>py main.py</code> works when <code>python</code> opens the store.</p>',
              '<p class="caption">Python 3.8 or newer is the entire list.</p>')
t = t.replace('<p class="fine">© 2026 Mahakam Moonlight Studio. The source is released under the MIT licence.</p>',
              '<p class="fine">© 2026 Mahakam Moonlight Studio, MIT licence.</p>')

# airy separation between the wells, like the game's own screens
old_gap = '.moments { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-4xl); }'
assert old_gap in t
t = t.replace(old_gap, '.moments { display: grid; grid-template-columns: minmax(0, 1fr); gap: calc(var(--space-4xl) * 2); }', 1)

old_deals = '.deals { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); }'
if old_deals in t:
    t = t.replace(old_deals,
                  '.deals { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-4xl); }', 1)

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('patched; size', len(t))
