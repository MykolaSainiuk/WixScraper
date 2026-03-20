import os

base = 'fgamlet.wixsite.com'
needle = 'margin-top: 0 !important'
marker = '.slick-carousel .slick-dots li.slick-active button:before {\n            color: #333;\n            opacity: 1;\n        }\n        '
addition = '#comp-ifqtfs8k { margin-top: 0 !important; }\n        '
patched = 0

for root, dirs, files in os.walk(base):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        path = os.path.join(root, fname)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if needle in content:
            continue
        if marker in content:
            new = content.replace(marker, marker + addition)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            patched += 1
            print(f'  Patched: {path}')

print(f'Done: {patched} files')
