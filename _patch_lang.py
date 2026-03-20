import glob

SCRIPT = """<script>
(function() {
    var langRoutes = { 'uk': '/', 'ru': '/ru/', 'pl': '/pl/' };
    function getCurrentLang() {
        var p = window.location.pathname;
        if (p === '/ru' || p.indexOf('/ru/') === 0) return 'ru';
        if (p === '/pl' || p.indexOf('/pl/') === 0) return 'pl';
        return 'uk';
    }
    function getPagePath() {
        var p = window.location.pathname;
        var cur = getCurrentLang();
        if (cur === 'uk') return p;
        var prefix = '/' + cur;
        return p.indexOf(prefix) === 0 ? (p.slice(prefix.length) || '/') : p;
    }
    var handle = document.querySelector('[data-testid="languages-dropdown-handle"]');
    var menu = document.querySelector('[data-testid="languages-dropdown-handle-container"] [role="menu"]');
    if (!handle || !menu) return;
    menu.style.display = 'none';
    handle.style.cursor = 'pointer';
    handle.addEventListener('click', function(e) {
        e.stopPropagation();
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', function() { menu.style.display = 'none'; });
    ['uk', 'ru', 'pl'].forEach(function(lang) {
        var opt = document.querySelector('[data-testid="dropdown-option-' + lang + '"]');
        if (!opt) return;
        opt.style.cursor = 'pointer';
        opt.addEventListener('click', function(e) {
            e.stopPropagation();
            var page = getPagePath();
            var root = langRoutes[lang];
            var target = root === '/' ? page : root + (page === '/' ? '' : page.replace(/^\\//, ''));
            window.location.href = target;
        });
    });
})();
</script>"""

base = '/Users/mykolasainiuk/volume3/WixScraper/fgamlet.wixsite.com'
for path in glob.glob(base + '/**/index.html', recursive=True):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if 'languages-dropdown-handle-container' in html and 'langRoutes' not in html:
        html = html.replace('</body>', SCRIPT + '</body>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print('patched:', path)
    elif 'langRoutes' in html:
        print('skip:', path)
    else:
        print('no lang menu:', path)
