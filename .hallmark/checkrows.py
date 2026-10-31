import sys
sys.stdout.reconfigure(encoding='utf-8')
t = open('docs/index.html', encoding='utf-8').read()
for frag in ['The yearly directive menu', 'The dossier listing', 'A flash crisis printed', 'collapse screen of a 1979']:
    i = t.find(frag)
    a = t.index('<pre aria-hidden="true">', i)
    b = t.index('</pre>', a)
    block = t[a:b]
    print(frag[:34], 'rows:', block.count('class="ln"'))
print('PATH in file:', t.count('PATH: not yet chosen'))
print('UNLEASH in file:', t.count('UNLEASH Kosygin'))
