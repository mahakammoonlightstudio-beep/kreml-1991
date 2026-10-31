import base64
import re

subsets = ['cyrillic-ext', 'cyrillic', 'latin-ext', 'latin']
ranges = {
    'cyrillic-ext': 'U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F',
    'cyrillic': 'U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116',
    'latin-ext': 'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF',
    'latin': 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD',
}
head = '''/* Martian Mono, embedded (OFL, built from fonts.google.com css2 v2026-10-30):
   variable axes wdth 75% 112.5% / wght 400 700, four subsets, one face each.
   The data URIs make the face load with the document itself in every protocol
   (file, http, Pages), so the first paint and its measurement share one metric. */
'''
blocks = []
for s in subsets:
    data = open(f'docs/assets/fonts/martian-mono-{s}.woff2', 'rb').read()
    b64 = base64.b64encode(data).decode()
    blocks.append(f'''/* {s} */
@font-face {{
  font-family: 'Martian Mono';
  font-style: normal;
  font-weight: 400 700;
  font-stretch: 75% 112.5%;
  font-display: block;
  src: url(data:font/woff2;base64,{b64}) format('woff2');
  unicode-range: {ranges[s]};
}}''')
    print(s, len(data), 'bytes')
css = head + '\n'.join(blocks) + '\n'
open('docs/assets/fonts.css', 'w', encoding='utf-8').write(css)
print('fonts.css', len(css), 'chars')
