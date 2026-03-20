# Import puppeteer
import json
from urllib.parse import urlparse
from pyppeteer import launch
import asyncio
import os
import requests
from PIL import Image

# Scroll to the bottom to load all content
async def scroll_to_bottom(page):
    pageHeight = await page.evaluate('document.body.scrollHeight')
    for i in range(0, pageHeight, 100):
        await page.evaluate(f'window.scrollTo(0, {i})')
        await asyncio.sleep(0.1)
    await asyncio.sleep(1)

# Only use this function in compliance with Wix Terms of Service. 
# Only use this function in compliance with Wix Terms of Service. 
async def delete_wix(page):
    # Delete the wix header with id WIX_ADS
    await page.evaluate('''() => {
        const element = document.getElementById('WIX_ADS');
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }''')

    # Edit in-line CSS defined in <style> tag, remove any string "--wix-ads"
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('style');
        for (const element of elements) {
            if (element && typeof element.innerText === 'string' && element.innerText.includes('--wix-ads')) {
                element.innerText = element.innerText.replace('--wix-ads', '');
            }
        }
    }''')

    # Delete any span that includes "Made with Wix"
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('span');
        for (const element of elements) {
            if (element && typeof element.innerText === 'string' && element.innerText.includes('Made with Wix') && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }
    }''')

    # Remove all <script> tags
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('script');
        for (const element of elements) {
            if (element && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }
    }''')

    # Remove all <link> tags
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('link');
        for (const element of elements) {
            if (element && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }
    }''')


async def fix_gallery(page):

    # If pro-gallery is a class on the page,
    # then we need to fix the gallery

    # Get the gallery element
    gallery = await page.querySelector('.pro-gallery')

    if(gallery != None):

        print("Found gallery! Fixing..")
        
        # Import slick.carousel
        await page.addScriptTag(url='https://cdn.jsdelivr.net/npm/jquery@3.6.4/dist/jquery.min.js')
        await page.addStyleTag(url='https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.css')
        await page.addStyleTag(url='https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick-theme.css')
        await page.addScriptTag(url='https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.js')

        # Get all img links
        img_links = await gallery.querySelectorAllEval('img', 'nodes => nodes.map(n => n.src)')
    
        # Create the carousel and insert it two parents above the gallery
        await page.evaluate('''() => {
            const element = document.createElement('div');
            element.className = 'slick-carousel';
            document.querySelector('.pro-gallery').parentNode.parentNode.insertBefore(element, document.querySelector('.pro-gallery').parentNode);
        }''')

        # Delete all siblings of the slick carousel
        await page.evaluate('''() => {
            const element = document.querySelector('.slick-carousel');
            while (element.nextSibling) {
                element.nextSibling.parentNode.removeChild(element.nextSibling);
            }
        }''')

        # Add the images to the carousel
        for link in img_links:
            await page.evaluate(f'''() => {{
                const element = document.createElement('img');
                element.src = '{link}';
                element.alt = 'Gallery Image';
                document.querySelector('.slick-carousel').appendChild(element);
            }}''')

        # Add the above evaluation as a script tag
        await page.addScriptTag(content='''
        window.addEventListener('DOMContentLoaded', function() {
        var $jq = jQuery.noConflict();
        $jq(document).ready(function () {
            $jq('.slick-carousel').slick({
                dots: true,
                infinite: true,
                speed: 300,
                slidesToShow: 2,
                responsive: [
                    {
                    breakpoint: 1024,
                    settings: {
                        slidesToShow: 1,
                    }
                    },
                    {
                    breakpoint: 600,
                    settings: {
                        slidesToShow: 1,
                    }
                    }
                ]
            });
        });
        });''')

async def fix_googlemap(page, mapData):

    # Get the one titled = "Google Maps"
    googlemap = await page.querySelector('wix-iframe[title="Google Maps"]')

    if(googlemap != None):

        print("Found Google Maps! Fixing..")

        # Import leaflet
        await page.addStyleTag(url='https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/leaflet.css')

        await page.evaluate('''() => {
            const element = document.createElement('script');
            element.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/leaflet.js';
            document.querySelector('script').parentNode.insertBefore(element, document.querySelector('script').nextSibling);
        }''')

        # Add new style tag to the page
        await page.addStyleTag(content='''
        #map { height: 100%; }

        html, body { height: 100%; margin: 0; padding: 0; }

        :root {
        
        --map-tiles-filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.7);

        }

        @media (prefers-color-scheme: dark) {
            .map-tiles {
                filter:var(--map-tiles-filter, none);
            }
        }''')

        # Add a new map div next to the google map
        await page.evaluate('''() => {
            const element = document.createElement('div');
            element.id = 'map';
            document.querySelector('iframe[title="Google Maps"]').parentNode.insertBefore(element, document.querySelector('iframe[title="Google Maps"]').nextSibling);
        }''')

        # Delete all siblings of the map div
        await page.evaluate('''() => {
            const element = document.querySelector('#map');
            while (element.nextSibling) {
                element.nextSibling.parentNode.removeChild(element.nextSibling);
            }
        }''')

        

        content = '''
        window.addEventListener('DOMContentLoaded', function() {

        var map = L.map('map').setView([''' + mapData['latitude'] + ',' + mapData['longitude'] + '],' + mapData['zoom'] + ''');

        // set tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
            className: 'map-tiles'
        }).addTo(map);

        // add marker
        L.marker([''' + mapData['mapMarker']['latitude'] + ',' + mapData['mapMarker']['longitude'] + ''']).addTo(map)
            .bindPopup(" ''' + mapData['mapMarker']['popup'] + ''' ")
            .openPopup();
            
        });'''

        # Instead of addScriptTag, append the entire above script as a <script> at the end of the body
        await page.evaluate('''() => {
            const element = document.createElement('script');
            element.innerHTML = `''' + content + '''`;
            document.querySelector('body').appendChild(element);
        }''')

        # Delete the google map iframe
        await page.evaluate('''() => {
            const element = document.querySelector('iframe[title="Google Maps"]');
            element.parentNode.removeChild(element);
        }''')      

        # Add preconnect to openstreetmap
        await page.evaluate('''() => {
            const element = document.createElement('link');
            element.rel = 'preconnect';
            element.href = 'https://a.tile.openstreetmap.org';
            document.querySelector('head').appendChild(element);
            element.href = 'https://b.tile.openstreetmap.org';
            document.querySelector('head').appendChild(element);
            element.href = 'https://c.tile.openstreetmap.org';
            document.querySelector('head').appendChild(element);
        }''')


async def fix_slideshow(page):

    # Get the gallery element
    gallery = await page.querySelector('.wixui-slideshow')

    if(gallery != None):

        print("Found Slideshow! Fixing..")
        
        # Import slick.carousel
        await page.addScriptTag(url='https://cdn.jsdelivr.net/npm/jquery@3.6.4/dist/jquery.min.js')
        await page.addStyleTag(url='https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.css')
        await page.addStyleTag(url='https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick-theme.css')
        await page.addScriptTag(url='https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.js')

        # Create the carousel and insert it two parents above the gallery
        await page.evaluate('''() => {
            const element = document.createElement('div');
            element.className = 'slick-carousel-slides';
            document.querySelector('.wixui-slideshow').parentNode.parentNode.insertBefore(element, document.querySelector('.wixui-slideshow').parentNode);
        }''')


        # Give all images inside slideshow alt tags
        await page.evaluate('''() => {
            const elements = document.querySelectorAll('nav[aria-label="Slides"] li img');
            for (const element of elements) {   
                element.alt = 'Slideshow Image';
            }
        }''')

        slides = await page.querySelectorAll('nav[aria-label="Slides"] li')

        # Ensure first slide is selected
        await asyncio.sleep(5)
        await slides[0].click()

        for slide in slides:

            await slide.click()
            await asyncio.sleep(5)

            #img_parents = await gallery.querySelectorAllEval('img', 'nodes => nodes.map(n => n.parentNode.parentNode.innerHTML)')
            slide_content = await page.querySelector('div[data-testid="slidesWrapper"] > div')

            # Get innerHTML of slide_content
            parent = await page.evaluate('(slide_content) => slide_content.innerHTML', slide_content)

            # Get all parents of img tags, iterate over and add them instead
            await page.evaluate(f'''(parent) => {{
                const element = document.createElement('div');
                element.innerHTML = parent;
                document.querySelector('.slick-carousel-slides').appendChild(element);
            }}''', parent)

        # Delete all children of slidesWrapper
        await page.evaluate('''() => {
            const element = document.querySelector('div[data-testid="slidesWrapper"]');
            while (element.firstChild) {
                element.removeChild(element.firstChild);
            }
        }''')


        # Move slick-carousel next to aria-label="Slideshow"
        await page.evaluate('''() => {
           const element = document.querySelector('.slick-carousel-slides');
           document.querySelector('.wixui-slideshow').parentNode.insertBefore(element, document.querySelector('.wixui-slideshow').nextSibling);
        }''')

        # Take the class and id from aria-label="Slideshow" and add it to slick-carousel, then delete aria-label="Slideshow"
        await page.evaluate('''() => {
           const element = document.querySelector('.wixui-slideshow');
           document.querySelector('.slick-carousel-slides').className = element.className + ' slick-carousel-slides';
           document.querySelector('.slick-carousel-slides').id = element.id;
           element.parentNode.removeChild(element);
        }''')

        # Make .slick-next class element have the style: right: 75px and .slick-prev class element have the style: left: 75px
        # using style tags
        await page.addStyleTag(content='''
        .slick-next {
            z-index: 100;
            right: 75px;
        }

        .slick-prev {
            z-index: 100;
            left: 75px;
        }''')




slideFix = '''<script>
        window.addEventListener('DOMContentLoaded', function() {
        var $jq = jQuery.noConflict();
        $jq(document).ready(function () {
            $jq('.slick-carousel-slides').slick({
                dots: true,
                infinite: false,
                speed: 300,
                slidesToShow: 1,
                responsive: [
                    {
                    breakpoint: 1024,
                    settings: {
                        slidesToShow: 1,
                    }
                    },
                    {
                    breakpoint: 600,
                    settings: {
                        slidesToShow: 1,
                    }
                    }
                ]
            });
        });
    });</script></body>'''

lightModeFix = '''<style>
        .slick-dots li button:before {
            font-family: 'slick';
            font-size: 6px;
            line-height: 20px;
            position: absolute;
            top: 0;
            left: 0;
            width: 20px;
            height: 20px;
            content: '•';
            text-align: center;
            opacity: .25;
            color: white;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .slick-dots li.slick-active button:before {
            opacity: .75;
            color: white;
        }
    </style></head>'''

async def makeLocalImages(page, hostname, forceDownloadAgain):
    from urllib.parse import unquote
    # Create images folder if it doesn't exist in hostname folder
    if not os.path.exists(hostname + '/images'):
        os.makedirs(hostname + '/images')

    # Collect all img src AND srcset URLs, stripping Wix resize suffixes (/v1/fill/...)
    imageLinks = await page.querySelectorAllEval('img', 'nodes => nodes.map(n => n.src)')
    srcsetLinks = await page.querySelectorAllEval(
        'img[srcset]',
        '''nodes => nodes.flatMap(n => n.srcset.split(',').map(s => s.trim().split(' ')[0]))'''
    )
    # For Wix CDN URLs, strip resize path so we download the full-res original
    def strip_wix_resize(url):
        if 'static.wixstatic.com/media/' in url:
            # Keep only up to the ~mv2.xxx part, drop /v1/fill/... suffix
            import re
            m = re.match(r'(https://static\.wixstatic\.com/media/[^/]+(?:~mv2\.[a-z]+)?)', url)
            if m:
                return m.group(1)
        return url
    allLinks = list(set(strip_wix_resize(u) for u in imageLinks + srcsetLinks))

    def download_image(link):
        imageName = unquote(link.split('/')[-1].split('?')[0])
        webpName = imageName.rsplit('.', 1)[0] + '.webp'
        if not forceDownloadAgain and os.path.exists(hostname + '/images/' + webpName):
            return
        try:
            r = requests.get(link, allow_redirects=True, timeout=15)
            r.raise_for_status()
            raw_path = hostname + '/images/' + imageName
            open(raw_path, 'wb').write(r.content)
            im = Image.open(raw_path)
            im.save(hostname + '/images/' + webpName, 'webp')
            os.remove(raw_path)
        except Exception as e:
            print(f'Warning: could not download image {link}: {e}')

    for link in allLinks:
        # Skip non-HTTP(S) URLs (e.g. data: URIs)
        if not link.startswith('http://') and not link.startswith('https://'):
            continue
        download_image(link)

    # Replace all image links with the local image links, using the webp format
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('img');
        for (const element of elements) {
            const name = decodeURIComponent(element.src.split('/').slice(-1)[0].split('?')[0]);
            const webpName = name.replace(/\\.[^.]+$/, '') + '.webp';
            element.src = '/images/' + webpName;
            element.removeAttribute('srcset');
        }
    }''')

async def makeJsLocal(hostname, forceDownloadAgain):
    """Download CDN JS files used by the carousel/slider to a local /js/ folder."""
    if not os.path.exists(hostname + '/js'):
        os.makedirs(hostname + '/js')

    js_files = [
        'https://cdn.jsdelivr.net/npm/jquery@3.6.4/dist/jquery.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.js',
    ]
    css_files = [
        'https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.css',
        'https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick-theme.css',
    ]

    for url in js_files + css_files:
        fname = url.split('/')[-1]
        ext_dir = hostname + '/js'
        dest = ext_dir + '/' + fname
        if not forceDownloadAgain and os.path.exists(dest):
            continue
        try:
            r = requests.get(url, allow_redirects=True, timeout=15)
            r.raise_for_status()
            open(dest, 'wb').write(r.content)
        except Exception as e:
            print(f'Warning: could not download {url}: {e}')


async def makeFontsLocal(page, hostname, forceDownloadAgain):
        # Make all fonts local
    # Create a fonts folder if it doesn't exist in hostname folder
    if not os.path.exists(hostname + '/fonts'):
        os.makedirs(hostname + '/fonts')

    # Download all fonts, which are parastorage links
    fontLinks = await page.querySelectorAllEval(
    'style',
    '''nodes => nodes
        .map(n => typeof n.innerText === 'string' ? n.innerText.match(/url\\((.*?)\\)/g) : [])
        .flat()
        .filter(x => x)'''
)


    # Get all url("//static.parastorage.com...") links
    fontLinks = [link for link in fontLinks if link is not None and 'static.parastorage.com' in link]

    for link in fontLinks:
        # Only get if the link is a font
        if('woff' not in link and 'woff2' not in link and 'ttf' not in link and 'eot' not in link and 'otf' not in link and 'svg' not in link):
            continue
        
        # Remove anything before the link
        link = link.split('static.parastorage.com')[1]
        link = 'static.parastorage.com' + link
        # Get the font name
        fontName = link.split('/')[-1].split(')')[0]
        # Remove any ? parameters
        fontName = fontName.split('?')[0]
        # Remove any # parameters
        fontName = fontName.split('#')[0]
        # Remove any "
        fontName = fontName.replace('"', '')
        
        # If the font already exists, skip it
        if(not forceDownloadAgain and os.path.exists(hostname + '/fonts/' + fontName)):
            continue
        
        r = requests.get("https://" + link, allow_redirects=True)
        open(hostname + '/fonts/' + fontName, 'wb').write(r.content)

    # Replace all font links with the local font links where the font file name is the last item after the last slash
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('style');
        for (const element of elements) {
            if (element && typeof element.innerText === 'string' && element.innerText.includes('static.parastorage.com')) {
                const fontLinks = element.innerText.match(/url\\((.*?)\\)/g);
                if (Array.isArray(fontLinks)) {
                    for (const link of fontLinks) {
                        if (
                            link.includes('woff') || link.includes('woff2') ||
                            link.includes('ttf') || link.includes('eot') ||
                            link.includes('otf') || link.includes('svg')
                        ) {
                            let fontName = link.substring(link.lastIndexOf('/') + 1, link.lastIndexOf(')'))
                                .split('?')[0].split('#')[0].replace(/\"/g, '');
                            element.innerText = element.innerText.replace(link, 'url(\"/fonts/' + fontName + '\")');
                        }
                    }
                }
            }
        }
    }''')


async def fix_page(page, wait, hostname, blockPrimaryFolder, darkWebsite, forceDownloadAgain, metatags, mapData):
    
    # Get the current page
    key = page.url.split(hostname)[1]

    print("Current page: " + key)
    
    await asyncio.sleep(wait)
    await scroll_to_bottom(page)
    await delete_wix(page)
    await fix_gallery(page)
    await fix_googlemap(page, mapData)
    await fix_slideshow(page)

    # Defer all scripts
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('script');
        for (const element of elements) {
            element.setAttribute('defer', '');
        }
    }''')

    # In every font-face, add   font-display: swap; by going into the innertext of styles and replacing @font-face { with @font-face { font-display: swap;
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('style');
        for (const element of elements) {
            if (element && typeof element.innerText === 'string' && element.innerText.includes('--wix-ads')) {
                element.innerText = element.innerText.replace('--wix-ads', '');
            }
        }
    }''')

    # Remove data-href from every style tag
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('style');
        for (const element of elements) {
            element.removeAttribute('data-href');
            element.removeAttribute('data-url');
        }
    }''')


    # Make all images local
    await makeLocalImages(page, hostname, forceDownloadAgain)

    # Make all fonts local
    await makeFontsLocal(page, hostname, forceDownloadAgain)

    # Download CDN JS/CSS files locally
    await makeJsLocal(hostname, forceDownloadAgain)

    # Meta fixes
    # Delete all meta tags
    await page.evaluate('''() => {
        const elements = document.querySelectorAll('meta');
        for (const element of elements) {
            element.parentNode.removeChild(element);
        }
    }''')


    if(key not in metatags):
        print("Warning: No metatags defined for this page. Using default metatags.")
        key = '/'
       
    title = metatags[key]['title']
    description = metatags[key]['description']
    keywords = metatags[key]['keywords']
    canonical = metatags[key]['canonical']
    image = metatags[key]['image']
    author = metatags[key]['author']

    await page.evaluate(f'''() => {{
        const element = document.createElement('title');
        element.innerText = '{title}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add meta for title
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'title';
        element.content = '{title}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add meta for og:title
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.property = 'og:title';
        element.content = '{title}';
        document.querySelector('head').appendChild(element);
    }}''')

    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'description';
        element.content = '{description}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add meta for og:description
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.property = 'og:description';
        element.content = '{description}';
        document.querySelector('head').appendChild(element);
    }}''')

    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'keywords';
        element.content = '{keywords}';
        document.querySelector('head').appendChild(element);
    }}''')

    await page.evaluate(f'''() => {{
        const element = document.createElement('link');
        element.rel = 'canonical';
        element.href = '{canonical}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add meta for og:url
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.property = 'og:url';
        element.content = '{canonical}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Twitter meta tags
    await page.evaluate('''() => {
        const element = document.createElement('meta');
        element.name = 'twitter:card';
        element.content = 'summary_large_image';
        document.querySelector('head').appendChild(element);
    }''')

    # Add twitter:url
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'twitter:url';
        element.content = '{canonical}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add twitter:title
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'twitter:title';
        element.content = '{title}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add twitter:description
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'twitter:description';
        element.content = '{description}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add twitter:image
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'twitter:image';
        element.content = '{image}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add og:image
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.property = 'og:image';
        element.content = '{image}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Author meta tag
    await page.evaluate(f'''() => {{
        const element = document.createElement('meta');
        element.name = 'author';
        element.content = '{author}';
        document.querySelector('head').appendChild(element);
    }}''')

    # Add og:type website
    await page.evaluate('''() => {
        const element = document.createElement('meta');
        element.property = 'og:type';
        element.content = 'website';
        document.querySelector('head').appendChild(element);
    }''')

    # Add new meta tags
    await page.evaluate('''() => {
        const element = document.createElement('meta');
        element.name = 'viewport';
        element.content = 'width=device-width, initial-scale=1.0';
        document.querySelector('head').appendChild(element);
    }''')

    await page.evaluate('''() => {
        const element = document.createElement('meta');
        element.setAttribute('charset', 'utf-8');
        document.querySelector('head').insertBefore(element, document.querySelector('head').firstChild);
    }''')

    await page.evaluate('''() => {
        const element = document.createElement('meta');
        element.name = 'robots';
        element.content = 'index, follow';
        document.querySelector('head').appendChild(element);
    }''')

    await page.evaluate('''() => {
        const element = document.createElement('meta');
        element.name = 'googlebot';
        element.content = 'index, follow';
        document.querySelector('head').appendChild(element);
    }''')


    # <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    await page.evaluate('''() => {
        const element = document.createElement('link');
        element.rel = 'apple-touch-icon';
        element.sizes = '180x180';
        element.href = '/apple-touch-icon.png';
        document.querySelector('head').appendChild(element);
    }''')

    # <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    await page.evaluate('''() => {
        const element = document.createElement('link');
        element.rel = 'icon';
        element.type = 'image/png';
        element.sizes = '32x32';
        element.href = '/favicon-32x32.png';
        document.querySelector('head').appendChild(element);
    }''')

    # <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    await page.evaluate('''() => {
        const element = document.createElement('link');
        element.rel = 'icon';
        element.type = 'image/png';
        element.sizes = '16x16';
        element.href = '/favicon-16x16.png';
        document.querySelector('head').appendChild(element);
    }''')

    # <link rel="manifest" href="/site.webmanifest">
    await page.evaluate('''() => {
        const element = document.createElement('link');
        element.rel = 'manifest';
        element.href = '/site.webmanifest';
        document.querySelector('head').appendChild(element);
    }''')




    html = await page.evaluate('document.documentElement.outerHTML')

    html = html.replace('<br>', '')
    html = html.replace('</body>', slideFix)
    if(darkWebsite):
        html = html.replace('</head>', lightModeFix)
    # Fix every href to be relative 
    html = html.replace('href="https://' + hostname, 'href="')
    html = html.replace('href="http://' + hostname, 'href="')
    html = html.replace('href="https://www.' + hostname, 'href="')
    html = html.replace('href="http://www.' + hostname, 'href="')
    html = html.replace('href="www.' + hostname, 'href="')
    html = html.replace('href="' + hostname, 'href="')

    # Remove the primaryFolder from any hrefs
    html = html.replace('href="/' + blockPrimaryFolder, 'href="')

    # Any empty hrefs are now root hrefs, replace them with /
    html = html.replace('href=""', 'href="/"')

    # Remove browser-sentry script
    html = html.replace('<script src="https://browser.sentry-cdn.com/6.18.2/bundle.min.js" defer></script>', '')
    html = html.replace('//static.parastorage.com', 'https://static.parastorage.com')

    # Replace CDN JS/CSS with local copies
    html = html.replace('https://cdn.jsdelivr.net/npm/jquery@3.6.4/dist/jquery.min.js', '/js/jquery.min.js')
    html = html.replace('https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.min.js', '/js/slick.min.js')
    html = html.replace('https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick.css', '/js/slick.css')
    html = html.replace('https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.9.0/slick-theme.css', '/js/slick-theme.css')

    # Passive listener fix for jquery touch events
    html = html.replace('<script src="/js/jquery.min.js" defer=""></script>',
    '''<script src="/js/jquery.min.js" defer=""></script><script>window.addEventListener('DOMContentLoaded', function() { jQuery.event.special.touchstart = { setup: function( _, ns, handle ) { this.addEventListener("touchstart", handle, { passive: !ns.includes("noPreventDefault") }); } }; jQuery.event.special.touchmove = { setup: function( _, ns, handle ) { this.addEventListener("touchmove", handle, { passive: !ns.includes("noPreventDefault") }); } }; jQuery.event.special.wheel = { setup: function( _, ns, handle ){ this.addEventListener("wheel", handle, { passive: true }); } }; jQuery.event.special.mousewheel = { setup: function( _, ns, handle ){ this.addEventListener("mousewheel", handle, { passive: true }); } }; });</script>''')

    # Add doctype HTML to start 
    html = '<!DOCTYPE html>' + html

    return html


# Define the main function
async def main():
    
    """ Variable Declarations """
    # Load the data in from the json file
    with open('config.json') as f:
        data = json.load(f)

    site = data['site']
    blockPrimaryFolder = data['blockPrimaryFolder']
    wait = data['wait']
    recursive = data['recursive'].lower() == 'true'
    darkWebsite = data['darkWebsite'].lower() == 'true'
    forceDownloadAgain = data['forceDownloadAgain'].lower() == 'true'
    metatags = data['metatags']
    mapData = data['mapData']

    # Get the hostname
    hostname = urlparse(site).hostname

    # Use microsoft edge as the browser, set width and height to 1920x1080
    browser = await launch(headless=False, defaultViewport= None, executablePath='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args=['--window-size=1920,1080'])
    
    page = await browser.newPage()
    await page.goto(site)
    
    print(site)

    # Fix the first page
    html = await fix_page(page, wait, hostname, blockPrimaryFolder, darkWebsite, forceDownloadAgain,metatags, mapData)

    if not os.path.exists(hostname):
        os.mkdir(hostname)

    with open(hostname + '/index.html', 'w', encoding="utf-8") as f:
        f.write(html)

    if(recursive): 
        seen = []
        # Recursively go through all the local links and save them to the directory
        async def save_links(page, links):
            # Delete all links that are not local
            links = [link for link in links if hostname in link]
            # Delete all links with hash
            links = [link for link in links if '#' not in link]
            links = set(links)
            #print(links)
            errors = {}
            for link in links:
                print(link)
                if link in seen:
                    continue

                try:

                    await page.goto(link)
                    
                    seen.append(link)

                    html = await fix_page(page, wait, hostname, blockPrimaryFolder, darkWebsite, forceDownloadAgain,metatags, mapData)

                    # Write each page as index.html to a folder named after the page
                    # Check if the hostname is nested inside another folder
                    # Count number of slashes
                    newlink = link.replace('https://', '').replace('http://', '')

                    if(newlink.count('/') > 1 and blockPrimaryFolder not in newlink.split('/')[1]):
                        # Create the folder
                        if not os.path.exists(hostname + '/' + '/'.join(newlink.split('/')[1:])):
                            os.makedirs(hostname + '/' + '/'.join(newlink.split('/')[1:]))
                        with open(hostname + '/' + '/'.join(newlink.split('/')[1:]) + '/index.html', 'w', encoding="utf-8") as f:
                            f.write(html)
                    else:
                        if not os.path.exists(hostname + '/' + link.split('/')[-1]):
                            os.makedirs(hostname + '/' + link.split('/')[-1])
                        with open(hostname + '/' + link.split('/')[-1] + '/index.html', 'w', encoding="utf-8") as f:
                            f.write(html)
                
                    await save_links(page, await page.querySelectorAllEval('a', 'nodes => nodes.map(n => n.href)'))

                except Exception as e:
                    
                    # Check the error count, if over 3, add link to the seen list (ignore)
                    if(link in errors):
                        errors[link] += 1
                    else:
                        errors[link] = 1

                    if(errors[link] > 3):
                        seen.append(link)
                        print("Error: " + link + ". Giving up after 3 attempts. Added to seen list.")
                        continue

                    print(e)
                    print("Error: " + link + ". Try " + str(errors[link]) + " of 3")

                    continue

        await save_links(page, await page.querySelectorAllEval('a', 'nodes => nodes.map(n => n.href)'))
        
    #await browser.close()

asyncio.run(main())

