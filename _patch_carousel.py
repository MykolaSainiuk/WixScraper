import glob, re

OLD_IMG = '<img src="/images/194c5d_17a625e617a7429383ad355847b0ac5a~mv2.webp" alt="Gallery Image">'
NEW_IMG = '<img src="/images/the porshe.jpg" alt="Gallery Image">'

base = '/Users/mykolasainiuk/volume3/WixScraper/fgamlet.wixsite.com'
for path in glob.glob(base + '/**/index.html', recursive=True):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if OLD_IMG in html and NEW_IMG not in html:
        # Insert new image before the old 2nd image (making it the new 2nd, old 2nd becomes 3rd)
        html = html.replace(OLD_IMG, NEW_IMG + OLD_IMG, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print('patched:', path)
    elif NEW_IMG in html:
        print('skip (already patched):', path)
    else:
        print('no carousel match:', path)
