import glob

OLD_CSS = '.slick-carousel {\n            position: relative;\n            padding-bottom: 40px;\n        }'
NEW_CSS = '''[data-hook="tpa-components-provider"] {
            height: auto !important;
            max-height: none !important;
            overflow: visible !important;
        }
        .slick-carousel {
            position: relative;
            padding-bottom: 40px;
            height: auto !important;
            max-height: none !important;
        }
        .slick-carousel .slick-list,
        .slick-carousel .slick-track,
        .slick-carousel .slick-slide,
        .slick-carousel .slick-slide > div {
            height: auto !important;
            max-height: none !important;
        }
        .slick-carousel img {
            width: 100%;
            height: auto !important;
            max-height: none !important;
            object-fit: contain !important;
            display: block;
        }'''

base = '/Users/mykolasainiuk/volume3/WixScraper/fgamlet.wixsite.com'
for path in glob.glob(base + '/**/index.html', recursive=True):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if OLD_CSS in html:
        html = html.replace(OLD_CSS, NEW_CSS, 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print('patched:', path)
    elif 'tpa-components-provider' in html and 'object-fit: contain' in html:
        print('skip (already patched):', path)
    else:
        print('no match:', path)
