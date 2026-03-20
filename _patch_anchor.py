import glob

SCRIPT = """<script>
(function() {
    var anchorMap = {
        'dataItem-ifmfwm07': 'comp-lddi5052',
        'dataItem-khqbpf7a': 'comp-khqbpf5q',
        'dataItem-ifmb0mhm1': 'comp-ifmb0mhm'
    };

    function smoothScrollTo(y, duration) {
        var start = window.pageYOffset;
        var dist = y - start;
        var t0 = null;
        function ease(t) { return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t; }
        function step(ts) {
            if (!t0) t0 = ts;
            var p = Math.min((ts - t0) / duration, 1);
            window.scrollTo(0, start + dist * ease(p));
            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    function scrollToEl(el) {
        var header = document.getElementById('SITE_HEADER');
        var hh = header ? header.offsetHeight : 0;
        var y = el.getBoundingClientRect().top + window.pageYOffset - hh;
        smoothScrollTo(y, 900);
    }

    document.addEventListener('click', function(e) {
        var a = e.target;
        while (a && a.tagName !== 'A') a = a.parentElement;
        if (!a || !a.getAttribute('data-anchor')) return;
        var targetId = anchorMap[a.getAttribute('data-anchor')];
        if (!targetId) return;
        var el = document.getElementById(targetId);
        if (!el) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        scrollToEl(el);
    }, true);

    document.addEventListener('click', function(e) {
        var a = e.target;
        while (a && a.tagName !== 'A') a = a.parentElement;
        if (!a) return;
        var li = a.closest('.wixui-dropdown-menu__item[data-index="0"]');
        if (!li) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        smoothScrollTo(0, 900);
    }, true);
})();
</script>"""

base = '/Users/mykolasainiuk/volume3/WixScraper/fgamlet.wixsite.com'
for path in glob.glob(base + '/**/index.html', recursive=True):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if 'data-anchor=' not in html:
        print('skip (no anchors):', path)
        continue
    if 'anchorMap' in html:
        print('skip (already patched):', path)
        continue
    html = html.replace('</body>', SCRIPT + '</body>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('patched:', path)
