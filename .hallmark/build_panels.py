# Build the verbatim pre-block rows for the landing sections, spliced from the
# engine capture files. Line numbers are 1-based into each capture.
import re

def read(name):
    return open(name, encoding='utf-8').read().split('\n')

flash = read('.hallmark/flash.txt')
dossier = read('.hallmark/dossier.txt')
death = read('.hallmark/death.txt')

def esc(s):
    return s.replace('&', '&amp;')

def row(i, text, style):
    style = style or 'plain'
    lead = len(text) - len(text.lstrip(' '))
    lead_txt = ' ' * lead
    body = text.lstrip(' ')
    if style == 'dim':
        inner = f'<span class="dim">{esc(body)}</span>'
    elif style == 'val':
        inner = f'<span class="val">{esc(body)}</span>'
    elif style == 'alarm':
        inner = f'<span class="alarm">{esc(body)}</span>'
    elif style == 'mark':
        body2, n = re.subn(r'^(❯|▸) ', r'<span class="bar">\1</span> ', body)
        assert n == 1, body
        inner = body2
        # special: the wall clock token
        inner = inner.replace('(⏱ 9s)', '<span class="alarm">(⏱ 9s)</span>')
    elif style == 'lock':
        m = re.match(r'(✖) (.*)$', body)
        assert m, body
        inner = f'<span class="dim">{m.group(1)}</span> {esc(m.group(2))}'
    elif style == 'plain':
        inner = esc(body)
    else:
        raise SystemExit('bad style')
    return f'{lead_txt}<span class="ln" style="--i:{i}">{inner}</span>'

def block(lines_spec, src):
    out = []
    for n, (ln, style) in enumerate(lines_spec):
        out.append(row(n, src[ln - 1], style))
    return out

panels = {}
panels['directive'] = block([
    (121, 'dim'),            # ── YEARLY DIRECTIVE ──
    (122, 'val'),            # Economy
    (123, 'plain'),          # 1. Five-Year Plan
    (124, 'plain'),          # 2. Consumer goods
    (126, 'plain'),          # 4. Oil & gas exports
    (132, 'val'),            # Society
    (134, 'plain'),          # 10. KGB crackdown
    (142, 'mark'),           # ❯ Directive of the year: 10
    (143, 'plain'),          # ( ECONOMY ▲1 | ORDER ▲7 ... )
    (144, 'mark'),           # ▸ Directive issued: KGB crackdown
], flash)

panels['vodka'] = block([
    (146, 'dim'),            # ┌ EVENT ┐
    (147, 'plain'),          # ☈ The Vodka Shortage
    (148, 'plain'),          # Distilleries ship crates...
    (149, 'dim'),            # └ box close
    (150, 'plain'),
    (151, 'plain'),
    (152, 'plain'),
    (153, 'plain'),
    (154, 'plain'),
    (155, 'plain'),
    (156, 'mark'),           # ❯ Your decision: (⏱ 9s) 1
    (157, 'plain'),          # ( ORDER ▲1 | FAITH ▼2 )
], flash)

panels['dossier'] = block([
    (50, 'dim'),             # ╔ box top
    (51, 'dim'),             # ║ DOSSIER title
    (52, 'dim'),             # ╚ box bottom
    (53, 'plain'),           # TIMELINE / MODE
    (54, 'plain'),           # PATH
    (66, 'dim'),             # ── OPEN ROADS ──
    (67, 'lock'),            # ✖ pipeline
    (68, 'lock'),            # ✖ gold
    (70, 'lock'),            # ✖ kosygin
    (75, 'mark'),            # ▸ purge AVAILABLE now
    (77, 'lock'),            # ✖ union treaty
], dossier)

panels['death'] = block([
    (1989, 'alarm'),         # ██ COLLAPSE, 1979 ██
    (1990, 'plain'),
    (1991, 'dim'),           # ══ rule
    (1994, 'plain'),         # Legacy score: 133 — Removed...
    (1995, 'plain'),
], death)

# install well, from the README quick start (my own staging of it)
def install_rows():
    return [
        row(0, 'git clone https://github.com/mahakammoonlightstudio-beep/kreml-1991.git', 'plain'),
        row(1, 'cd kreml-1991', 'dim'),
        row(2, 'python main.py', 'val'),
    ]
panels['install'] = install_rows()

with open('.hallmark/panels.py.out', 'w', encoding='utf-8', newline='\n') as f:
    for key, rows in panels.items():
        f.write(f'==={key}===\n')
        f.write('\n'.join(rows) + '\n')
print('built')
for k, v in panels.items():
    print(k, len(v), 'rows')
