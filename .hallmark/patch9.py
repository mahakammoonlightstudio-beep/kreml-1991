# Patch pass 9 on docs/play/index.html:
# 1) title dash removed (gate 19 sees the title element)
# 2) disabled states get ink+fill+cursor channels instead of opacity alone (39a)
# 3) SGR screen colours derive from shared tokens via color-mix, no literals (48)
# 4) .panel declares its text colour (41)
# 5) group heads become h2 so the level ladder is h1 then h2 (F21)
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'docs/play/index.html'
t = open(path, encoding='utf-8').read()

old = '<title>Play КРЕМЛЬ 1991 in your browser — Soviet alternate-history game</title>'
new = '<title>Play КРЕМЛЬ 1991 in your browser: the real Python game</title>'
assert old in t
t = t.replace(old, new, 1)

old = '.btn:disabled { opacity: 0.5; cursor: wait; transform: none; }'
new = '.btn:disabled { background: var(--color-paper-3); color: var(--color-muted); border-color: var(--color-rule); cursor: wait; transform: none; }\n.btn.ghost:disabled { background: transparent; color: var(--color-muted); border-color: var(--color-rule); cursor: wait; }'
assert old in t
t = t.replace(old, new, 1)

old = '#line:disabled { opacity: 0.55; }'
new = '#line:disabled { color: var(--color-muted); background: var(--color-paper-3); cursor: not-allowed; }'
assert old in t
t = t.replace(old, new, 1)

oldsgr = '''#screen .r { color: oklch(72% 0.16 25); }
#screen .g { color: var(--color-accent); }
#screen .y { color: oklch(82% 0.13 95); }
#screen .b { color: oklch(74% 0.11 240); }
#screen .m { color: oklch(76% 0.12 320); }
#screen .c { color: oklch(80% 0.1 195); }
#screen .w { color: oklch(98% 0.01 140); }'''
newsgr = '''#screen .r { color: var(--color-error); }
#screen .g { color: var(--color-accent); }
#screen .y { color: color-mix(in oklab, var(--color-accent) 45%, var(--color-error)); }
#screen .b { color: color-mix(in oklab, var(--color-accent) 18%, var(--color-ink)); }
#screen .m { color: color-mix(in oklab, var(--color-accent) 35%, var(--color-ink-2)); }
#screen .c { color: color-mix(in oklab, var(--color-accent) 55%, var(--color-ink)); }
#screen .w { color: var(--color-ink); }'''
assert oldsgr in t
t = t.replace(oldsgr, newsgr, 1)

old = '.panel { background: var(--color-paper-2); border: var(--rule-hair) solid var(--color-rule); padding: var(--space-xl); }'
new = '.panel { background: var(--color-paper-2); border: var(--rule-hair) solid var(--color-rule); padding: var(--space-xl); color: var(--color-ink); }'
assert old in t
t = t.replace(old, new, 1)

old = '.group h3 { font-size: var(--text-xs); font-weight: var(--display-weight); color: var(--color-muted); margin-block-end: var(--space-xs); }'
new = '.group h2 { font-size: var(--text-xs); font-weight: var(--display-weight); font-stretch: var(--stretch-display); color: var(--color-muted); margin-block: 0 var(--space-xs); }'
assert old in t
t = t.replace(old, new, 1)

t = t.replace('<h3>Difficulty</h3>', '<h2>Difficulty</h2>', 1)
t = t.replace('<h3>Timeline</h3>', '<h2>Timeline</h2>', 1)

open(path, 'w', encoding='utf-8', newline='\n').write(t)
print('patched; size', len(t))
