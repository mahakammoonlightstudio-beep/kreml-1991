# Patch pass 7: drop the per-table h3s (the column heads carry the context),
# zero the table's top margin, tabula rasa for the terminal ledger.
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'docs/index.html'
t = open(path, encoding='utf-8').read()
n1 = t.count('<h3>The drift you accept</h3>')
n2 = t.count('<h3>The year you inherit</h3>')
t = t.replace('<h3>The drift you accept</h3>', '')
t = t.replace('<h3>The year you inherit</h3>', '')
print('h3s removed:', n1, n2)

t = t.replace('.deal table { width: 100%; border-collapse: collapse; margin-block-start: var(--space-md); font-size: var(--text-sm); font-variant-numeric: tabular-nums; }',
              '.deal table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); font-variant-numeric: tabular-nums; }')

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('patched; size', len(t))
