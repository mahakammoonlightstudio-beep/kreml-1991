import sys
sys.stdout.reconfigure(encoding='utf-8')
t = open('docs/index.html', encoding='utf-8').read()
print('lines', t.count('\n') + 1)
keys = ['section class="loop"', 'section class="yardstick"', 'section class="close"',
        'footer class="colophon"', 'data-print', 'The Vodka Shortage', 'COLLAPSE, 1979',
        'KGB crackdown', 'THE SYSTEM ITSELF', 'python main.py', 'MIT licence', '</html>',
        'aria-label="The yearly directive menu', 'moment-head', 'nav-links']
for k in keys:
    print(k, '->', t.count(k))
