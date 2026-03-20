import re
with open('/Users/mykolasainiuk/volume3/WixScraper/fgamlet.wixsite.com/index.html', encoding='utf-8') as f:
    html = f.read()

idx = html.find('data-hook="tpa-components-provider"')
snippet = html[max(0,idx-4000):idx]
divs = re.findall(r'<(?:div|section)[^>]+class="([^"]+)"', snippet)
print("=== PARENT CLASSES ===")
for d in divs[-10:]:
    print(repr(d[:100]))

# Find the section component ID wrapping the gallery
comp_ids = re.findall(r'id="(comp-[^"]+)"', snippet)
print("\n=== COMP IDs ===")
for c in comp_ids[-5:]:
    print(c)

# Search CSS for height rules on those comp IDs
styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
full_css = '\n'.join(styles)
print("\n=== HEIGHT CSS FOR COMP IDs ===")
for cid in comp_ids[-5:]:
    short = cid[:15]
    for m in re.finditer(r'[^}]*' + re.escape(short) + r'[^{]*\{[^}]*height[^}]*\}', full_css):
        print(m.group(0).strip()[:300])
        print('---')
