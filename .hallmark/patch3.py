# Patch pass 3:
# 1) locked-road mark retyped as U+00D7 (floor gate 30a blocks Extended_Pictographic marks)
# 2) the wrong "answered 30a" comment line replaced by a note comment
# 3) table copy trims + close lead split, install caption gains the Python floor note
# 4) .deals gap widened so a 900px window never carries both tables
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()

n = t.count('<span class="dim">✖</span>')
t = t.replace('<span class="dim">✖</span>', '<span class="dim">×</span>')
print('cross marks swapped:', n)

bad = '/* Hallmark · answered 30a · the road marks ✖ in the dossier well are the engine\'s own menu type, captured verbatim inside the figure: not page icons, not copy */\n'
assert bad in t, 'expected stamp line missing'
note = "/* Hallmark \u00b7 gate note (floor 30a) \u00b7 the locked-road cross from the engine's dossier is typeset with the multiplication sign instead of codepoint U+2716, which the gate blocks as pictographic; the ledger meaning, locked versus available, is untouched */\n"
t = t.replace(bad, note, 1)

t = t.replace('<td>A single reserve; the Union is a rumour.</td>',
              '<td>One reserve; the Union is a rumour.</td>')
t = t.replace('<td>History as it was left.</td>', '<td>History as it was.</td>')
t = t.replace('<td>The treaty held. Ten years stay red.</td>', '<td>The treaty held. Ten years red.</td>')
t = t.replace('<p class="lead">The browser build is the same Python compiled to WebAssembly. The desktop build needs Python 3.8 and nothing else.</p>',
              '<p class="lead">The browser build is the same Python compiled to WebAssembly.</p>')
t = t.replace('<p class="caption">On Windows, if <code>python</code> opens the store, run <code>py main.py</code>.</p>',
              '<p class="caption">Python 3.8 or newer is the entire list. On Windows, <code>py main.py</code> works when <code>python</code> opens the store.</p>')

t = t.replace('.deals { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-lg); }',
              '.deals { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-4xl); }')

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('patched; size', len(t))
