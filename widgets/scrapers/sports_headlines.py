import os.path
import pathlib
import sys
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup
from pylatexenc.latexencode import unicode_to_latex
from base import CACHE_DIR

BASE_URLS = {'sports': 'https://apnews.com/sports'}
BBC_SPORTS_RSS = 'https://feeds.bbci.co.uk/sport/rss.xml'
MAX_HEADLINES = 3


def get_headlines(soup, max_count=MAX_HEADLINES):
    if max_count <= 0:
        return []
    main = soup.find('main')
    if main is None:
        raise RuntimeError('AP News main content is missing; check for a blocked response.')
    headlines, seen = [], set()
    # Match titles, not entire cards (which also include dates and summaries).
    for link in main.select('.PagePromo-title a[href]'):
        href = link['href']
        if '/article/' not in href:
            continue
        title = link.select_one('.PagePromoContentIcons-text') or link
        text = title.get_text(' ', strip=True)
        if not text or text.casefold() in seen:
            continue
        seen.add(text.casefold())
        headlines.append(unicode_to_latex(text))
        if len(headlines) >= max_count:
            break
    if not headlines:
        raise RuntimeError('No AP sports headlines found; the page markup may have changed.')
    return headlines


def render_headlines(headlines):
    if not headlines:
        return ''
    return ('\\begin{enumerate}\n'
            + '\n'.join('\\item ' + line for line in headlines)
            + '\n\\end{enumerate}\n')


def render(headlines, outfile):
    path = pathlib.Path(outfile)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = render_headlines(headlines)
    path.write_text(out, encoding='utf-8')
    return out


def get_rss_headlines(content, max_count=MAX_HEADLINES):
    if max_count <= 0:
        return []
    try:
        root = ET.fromstring(content)
    except ET.ParseError as error:
        raise RuntimeError('Sports feed did not return valid RSS XML.') from error
    headlines, seen = [], set()
    for item in root.findall('./channel/item'):
        title = ' '.join((item.findtext('title') or '').split())
        if title and title.casefold() not in seen:
            seen.add(title.casefold())
            headlines.append(unicode_to_latex(title))
        if len(headlines) >= max_count:
            break
    if not headlines:
        raise RuntimeError('Sports RSS feed contains no headlines.')
    return headlines


def _parse_content(content):
    # The cache may contain either the AP page or the fallback RSS feed.
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        root = None
    if root is not None and root.tag == 'rss':
        return get_rss_headlines(content)
    return get_headlines(BeautifulSoup(content, 'html.parser'))


def main(name='sports', cached=True, outdir=CACHE_DIR, source='ap'):
    if name not in BASE_URLS:
        raise ValueError(f'Unknown news category: {name}')
    if source not in ('ap', 'bbc'):
        raise ValueError("source must be 'ap' or 'bbc'")
    cache_path = pathlib.Path(CACHE_DIR) / f'{name}-news-{source}-v3.txt'
    headlines = None
    if cached and cache_path.exists():
        try:
            headlines = _parse_content(cache_path.read_text(encoding='utf-8'))
        except (RuntimeError, OSError, ValueError):
            pass
    if headlines is None:
        sources = [('BBC Sport', BBC_SPORTS_RSS)]
        if source == 'ap':
            sources.insert(0, ('AP', BASE_URLS[name]))
        errors = []
        for label, url in sources:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                headlines = _parse_content(response.content)
            except (requests.RequestException, RuntimeError, ValueError) as error:
                errors.append(f'{label}: {error}')
                continue
            if errors:
                print(f'AP sports unavailable; using {label} RSS. '
                      + ' | '.join(errors), file=sys.stderr)
            break
        else:
            raise RuntimeError('Could not retrieve sports headlines: ' + ' | '.join(errors))
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(response.text, encoding='utf-8')
    return render(headlines, os.path.join(outdir, f'{name}-news.tex'))


if __name__ == '__main__':
    main()
