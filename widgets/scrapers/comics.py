import io
import json
import os.path
import pathlib
import random
import sys
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PIL import Image
from base import CACHE_DIR

CACHE_PATH = os.path.join(CACHE_DIR, 'comic-{}.html')
BASE_URLS = {
    'xkcd': 'https://xkcd.com/',
    'calvinandhobbes': 'https://positron11.github.io/watterson/',
    'pearls': 'https://www.arcamax.com/thefunnies/pearlsbeforeswine/',
}
CALVIN_FIRST = date(1985, 11, 18)
CALVIN_LAST = date(1995, 12, 31)
CALVIN_EPOCH = date(2024, 1, 27)


def _today():
    return datetime.today().date()


def calvin_date_for_day(day=None):
    """A repeatable daily choice; visit every archive date before repeating."""
    day = _today() if day is None else day
    count = (CALVIN_LAST - CALVIN_FIRST).days + 1
    indices = list(range(count))
    random.Random(666).shuffle(indices)
    index = indices[(day - CALVIN_EPOCH).days % count]
    return CALVIN_FIRST + timedelta(days=index)


def _png(binary):
    """Decode actual image data and convert the first frame to PNG."""
    with Image.open(io.BytesIO(binary)) as image:
        image.seek(0)
        image.load()
        image = image.convert('RGBA' if 'transparency' in image.info
                              or image.mode == 'RGBA' else 'RGB')
        output = io.BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()


def _download_image(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    # Decoding rejects HTML/error pages even if the server returns HTTP 200.
    return _png(response.content)


def _image_tag(soup, name):
    if name == 'xkcd':
        return soup.select_one('#comic img')
    if name == 'pearls':
        return soup.select_one('img#comic-zoom')
    raise ValueError(f'Unknown HTML comic source: {name}')


def get_comic(soup, name):
    if name == 'calvinandhobbes':
        strip_date = calvin_date_for_day()
        url = urljoin(BASE_URLS[name], f'Comic/{strip_date:%Y%m%d}.gif')
        return {'url': url, 'binary': _download_image(url), 'ext': '.png',
                'date': strip_date.isoformat()}
    if name not in BASE_URLS:
        raise ValueError(f'Unknown comic: {name}')
    image = _image_tag(soup, name)
    if image is None or not image.get('src'):
        raise RuntimeError(f'No {name} comic image found; the page may be blocked or changed.')
    url = urljoin(BASE_URLS[name], image['src'])
    return {'url': url, 'binary': _download_image(url), 'ext': '.png',
            'caption': image.get('title', '')}


def render(item, outfile):
    if not item.get('binary'):
        raise ValueError('Comic image data is missing.')
    # Keep the original output convention: outfile is an extensionless stem.
    path = pathlib.Path(str(outfile) + '.png')
    binary = _png(item['binary'])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(binary)
    return str(path)


def _cached_page(name, cache_path=CACHE_PATH):
    path = pathlib.Path(cache_path.format(name))
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        # Ignore old undated caches, which could otherwise persist forever.
        if isinstance(data, dict) and data.get('date') == _today().isoformat():
            return data.get('content')
    except (OSError, ValueError):
        pass
    return None


def is_cached(name, cache_path=CACHE_PATH):
    return _cached_page(name, cache_path) is not None


def load_cached(name, cache_path=CACHE_PATH):
    content = _cached_page(name, cache_path)
    if content is None:
        raise ValueError(f'No valid page cache for {name} today.')
    return content


def fetch_comic(name, base_url, cache_path=CACHE_PATH):
    response = requests.get(base_url, timeout=30)
    response.raise_for_status()
    content = response.text
    soup = BeautifulSoup(content, 'html.parser')
    if _image_tag(soup, name) is None:
        raise RuntimeError(f'No {name} comic found at {base_url}; response not cached.')
    path = pathlib.Path(cache_path.format(name))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'date': _today().isoformat(), 'content': content}),
                    encoding='utf-8')
    return content


def main(name, outdir=CACHE_DIR, cached=True):
    if name not in BASE_URLS:
        raise ValueError(f'Unknown comic: {name}. Choose from: {", ".join(BASE_URLS)}')
    # Cache the decoded image too: a second run today needs no network requests.
    image_cache = pathlib.Path(CACHE_DIR) / 'comics-v2' / f'{_today()}-{name}.png'
    item = None
    if cached and image_cache.exists():
        try:
            binary = _png(image_cache.read_bytes())
        except (OSError, ValueError):
            pass
        else:
            item = {'binary': binary}
    if item is None:
        if name == 'calvinandhobbes':
            item = get_comic(None, name)
        else:
            content = None
            if cached:
                content = _cached_page(name)
                if content is not None and _image_tag(BeautifulSoup(content, 'html.parser'), name) is None:
                    content = None
            if content is None:
                content = fetch_comic(name, BASE_URLS[name])
            item = get_comic(BeautifulSoup(content, 'html.parser'), name)
        image_cache.parent.mkdir(parents=True, exist_ok=True)
        image_cache.write_bytes(item['binary'])
    return render(item, os.path.join(outdir, 'comic-' + name))


if __name__ == '__main__':
    failures = []
    for comic_name in BASE_URLS:
        try:
            main(comic_name, cached=True)
        except (requests.RequestException, OSError, ValueError, RuntimeError) as error:
            failures.append(comic_name)
            print(f'{comic_name}: {error}', file=sys.stderr)
    if failures:
        raise SystemExit(1)
