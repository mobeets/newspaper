import json
import os.path
import pathlib
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pylatexenc.latexencode import UnicodeToLatexEncoder
from base import CACHE_DIR

u = UnicodeToLatexEncoder(unknown_char_policy='ignore')
unicode_to_latex = u.unicode_to_latex
BASE_URLS = {'music': 'https://pitchfork.com/reviews/best/albums/'}


class PitchforkReview:
    def __init__(self, url=BASE_URLS['music'], cache_file='music-news', try_cache=True):
        self.url = url
        self.cache_path = pathlib.Path(CACHE_DIR) / (cache_file + '-v2.html')
        self.soup = None
        if try_cache and self.cache_path.exists():
            candidate = self.parse(self.cache_path.read_text(encoding='utf-8'))
            if candidate.select('.summary-item'):
                self.soup = candidate
        if self.soup is None:
            content = self.fetch(url)
            self.soup = self.parse(content)
            if not self.soup.select('.summary-item'):
                raise RuntimeError('No Pitchfork reviews found; the response may be blocked or markup changed.')
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(content, encoding='utf-8')

    @staticmethod
    def fetch(url):
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text

    @staticmethod
    def parse(content):
        return BeautifulSoup(content, 'html.parser')

    @staticmethod
    def _date(item):
        tag = item.select_one('time')
        if tag is None:
            raise RuntimeError('Pitchfork review is missing its publication date.')
        text = tag.get('datetime') or tag.get_text(' ', strip=True)
        try:
            return datetime.fromisoformat(text.replace('Z', '+00:00')).date()
        except ValueError:
            for fmt in ('%B %d, %Y', '%b %d, %Y', '%B %d %Y'):
                try:
                    return datetime.strptime(text, fmt).date()
                except ValueError:
                    pass
        raise RuntimeError(f'Unrecognized Pitchfork publication date: {text!r}')

    def is_new(self, item):
        # Preserve the original behavior: only yesterday's Best New Albums.
        return self._date(item) == (datetime.now() - timedelta(days=1)).date()

    def get(self):
        items = self.soup.select('.summary-item')
        if not items:
            raise RuntimeError('No Pitchfork review cards found.')
        item = next((card for card in items if self.is_new(card)), None)
        if item is None:
            return {}

        def text(selector):
            tag = item.select_one(selector)
            return tag.get_text(' ', strip=True) if tag else ''

        link = item.select_one('a.summary-item__hed-link[href], a[href*="/reviews/albums/"]')
        if link is None:
            raise RuntimeError('Pitchfork review card is missing its album link.')
        url = urljoin(self.url, link['href'])
        soup = self.parse(self.fetch(url))
        summary = ''

        def descriptions(value):
            if isinstance(value, dict):
                types = value.get('@type', [])
                if any(t in ('Review', 'Article', 'MusicReview') for t in
                       (types if isinstance(types, list) else [types])):
                    if value.get('description'):
                        yield value['description']
                for child in value.values():
                    yield from descriptions(child)
            elif isinstance(value, list):
                for child in value:
                    yield from descriptions(child)

        for tag in soup.select('script[type="application/ld+json"]'):
            try:
                summary = next(descriptions(json.loads(tag.get_text())), '')
            except ValueError:
                continue
            if summary:
                break
        if not summary:
            meta = soup.select_one('meta[property="og:description"], meta[name="description"]')
            summary = meta.get('content', '').strip() if meta else ''
        if not summary:
            raise RuntimeError(f'No review summary found at {url}')
        artist, album = text('.summary-item__sub-hed'), text('.summary-item__hed')
        if not artist or not album:
            raise RuntimeError('Pitchfork artist or album title is missing.')
        return {'artist': artist, 'album': album,
                'genre': text('.summary-item__rubric'), 'url': url,
                'summary': ' '.join(summary.split())}

    def render(self, item, outfile):
        out = ''
        if item:
            out = r"\textbf{Pitchfork's Best New Album}: "
            out += r'\textit{' + unicode_to_latex(item['album']) + '}'
            out += ' by ' + unicode_to_latex(item['artist'])
            if item.get('genre'):
                out += ' [' + unicode_to_latex(item['genre']) + ']'
            out += ': ' + unicode_to_latex(item['summary'])
        if outfile is not None:
            path = pathlib.Path(outfile)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(out, encoding='utf-8')
        else:
            print(out)
        return out


def main(name='music', cached=True, outdir=CACHE_DIR):
    sc = PitchforkReview(url=BASE_URLS[name], cache_file=f'{name}-news', try_cache=cached)
    sc.render(sc.get(), os.path.join(outdir, f'{name}-news.tex'))


if __name__ == '__main__':
    main(cached=False)
