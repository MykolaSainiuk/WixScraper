import re

with open('fgamlet.wixsite.com/index.html') as f:
    content = f.read()

# Find all occurrences of 122 near comp-ifqtfs8k
for m in re.finditer(r'.{0,200}comp-ifqtfs8k.{0,200}', content):
    if '122' in m.group():
        print(repr(m.group()))
        print('---')

# Also just search for 122px close to each other
idx = 0
while True:
    idx = content.find('comp-ifqtfs8k', idx)
    if idx < 0:
        break
    chunk = content[max(0,idx-100):idx+300]
    if '122' in chunk:
        print('AT', idx, repr(chunk[:200]))
    idx += 1
