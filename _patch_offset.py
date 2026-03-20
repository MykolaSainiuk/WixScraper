import glob

OLD = (
    "    function scrollToEl(el) {\n"
    "        var header = document.getElementById('SITE_HEADER');\n"
    "        var hh = header ? header.offsetHeight : 0;\n"
    "        var y = el.getBoundingClientRect().top + window.pageYOffset - hh;\n"
    "        smoothScrollTo(y, 900);\n"
    "    }"
)

NEW = (
    "    function scrollToEl(el, extra) {\n"
    "        var header = document.getElementById('SITE_HEADER');\n"
    "        var hh = header ? header.offsetHeight : 0;\n"
    "        var y = el.getBoundingClientRect().top + window.pageYOffset - hh + (extra || 0);\n"
    "        smoothScrollTo(y, 900);\n"
    "    }"
)

OLD2 = "        scrollToEl(el);"
NEW2 = "        scrollToEl(el, a.getAttribute('data-anchor') === 'dataItem-ifmfwm07' ? 200 : 0);"

base = '/Users/mykolasainiuk/volume3/WixScraper/fgamlet.wixsite.com'
for path in glob.glob(base + '/**/index.html', recursive=True):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if 'anchorMap' not in html:
        continue
    if OLD not in html:
        print('skip (mismatch or already updated):', path)
        continue
    html = html.replace(OLD, NEW).replace(OLD2, NEW2)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('patched:', path)
