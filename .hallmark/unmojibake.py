raw = open('docs/index.html', 'rb').read()
# Reverse the PowerShell 5.1 cp1252 roundtrip: decode the (BOM-prefixed) UTF-8,
# then re-encode each char as its original cp1252 byte. cp1252 has holes at
# 0x81 0x8D 0x8F 0x90 0x9D whose decode-side chars map straight back.
hole = {'\x81': b'\x81', '\x8d': b'\x8d', '\x8f': b'\x8f', '\x90': b'\x90', '\x9d': b'\x9d'}
s = raw.decode('utf-8-sig')
out = bytearray()
ok = True
for ch in s:
    if ch in hole:
        out += hole[ch]
        continue
    try:
        out += ch.encode('cp1252')
    except UnicodeEncodeError:
        print('UNMAPPED char at %d: %r' % (len(out), ch))
        ok = False
print('holes hit:', [hex(ord(c)) for c in s if c in hole][:12])
for probe in ['YEAR 1964', 'КРЕМЛЬ', '☭', 'The Union is yours.', 'Play in the browser', 'Gosplan',
              '<!DOCTYPE html>', 'hallmark', 'session', 'mandate']:
    print(probe, '->', 'OK' if probe in out.decode('utf-8', errors='replace') else 'MISSING')
if ok:
    open('docs/index.html', 'wb').write(bytes(out))
    print('rewritten, bytes:', len(out))
else:
    print('NOT rewritten; bytes kept only in memory')
