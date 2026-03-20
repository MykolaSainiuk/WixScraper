import requests, re, os

# Fetch original comp heights from all language variants on the live Wix site
urls = [
    'https://fgamlet.wixsite.com/12345',
    'https://fgamlet.wixsite.com/12345/general-9',
    'https://fgamlet.wixsite.com/12345/mkrvmotors',
    'https://fgamlet.wixsite.com/12345?lang=uk',
    'https://fgamlet.wixsite.com/12345?lang=pl',
    'https://fgamlet.wixsite.com/12345/general-9?lang=uk',
    'https://fgamlet.wixsite.com/12345/general-9?lang=pl',
]

comp_heights = {}
for url in urls:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        matches = re.findall(r'(#comp-[a-z0-9]+)\{([^}]*height:\d+px[^}]*)\}', r.text)
        for comp_id, props in matches:
            if comp_id not in comp_heights:
                h = re.search(r'height:(\d+px)', props)
                if h:
                    comp_heights[comp_id] = h.group(1)
        print(f'  {url}: found {len(matches)} rules')
    except Exception as e:
        print(f'  Error {url}: {e}')

print(f'\nTotal unique comp heights: {len(comp_heights)}')

# Patch all local HTML files: restore height:auto -> height:Xpx (except comp-kkohl36g)
base = 'fgamlet.wixsite.com'
patched_files = 0
patched_rules = 0

for root, dirs, files in os.walk(base):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        path = os.path.join(root, fname)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        new_content = content
        for comp_id, orig_height in comp_heights.items():
            if comp_id == '#comp-kkohl36g':
                continue  # keep this one as auto (gallery height fix)
            # Replace height:auto in this comp's CSS rule
            pattern = r'(' + re.escape(comp_id) + r'\{[^}]*)(height:auto)(;[^}]*\})'
            replacement = r'\g<1>height:' + orig_height + r'\g<3>'
            new_content, n = re.subn(pattern, replacement, new_content)
            patched_rules += n

        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            patched_files += 1
            print(f'  Patched: {path}')

print(f'\nDone: {patched_files} files, {patched_rules} rules restored')
