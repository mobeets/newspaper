import json
import os.path
import pathlib
import random
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pylatexenc.latexencode import unicode_to_latex
from base import CACHE_DIR

HISTORY_PATH = os.path.join(CACHE_DIR, 'movies_shown.txt')
CACHE_PATH = os.path.join(CACHE_DIR, 'movie_list.html')
MAX_SUMMARY_LEN = 200
BASE_URL = 'https://www.rottentomatoes.com/browse/movies_at_home/affiliates:amazon_prime,apple_tv_plus,disney_plus,max_us,netflix~sort:audience_highest'
BASE_MOVIE_URL = 'https://www.rottentomatoes.com'


def load_history(history_path=HISTORY_PATH):
    path = pathlib.Path(history_path)
    return path.read_text(encoding='utf-8').splitlines() if path.exists() else []


def update_history(new_movie, history_path=HISTORY_PATH):
    names = load_history(history_path)
    name = new_movie.get('name', '')
    if name and name not in names:
        names.append(name)
    path = pathlib.Path(history_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(names), encoding='utf-8')


def pick_movie(movie_list):
    if not movie_list:
        raise RuntimeError('No movies found; the listing may have changed or been blocked.')
    previous = set(load_history())
    return next((item for item in movie_list if item['name'] not in previous),
                None) or random.choice(movie_list)


def is_cached(cache_path=CACHE_PATH):
    return pathlib.Path(cache_path).exists()


def load_cached(cache_path=CACHE_PATH):
    content = pathlib.Path(cache_path).read_text(encoding='utf-8')
    # Support the original JSON-encoded HTML cache as well as plain HTML.
    try:
        decoded = json.loads(content)
    except ValueError:
        return content
    return decoded if isinstance(decoded, str) else content


def fetch(base_url=BASE_URL, cache_path=CACHE_PATH, save_cache=True):
    response = requests.get(base_url, timeout=30)
    response.raise_for_status()
    content = response.text
    if save_cache:
        # Never replace a good listing cache with a challenge/error page.
        get_movie_list(BeautifulSoup(content, 'html.parser'))
        path = pathlib.Path(cache_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content), encoding='utf-8')
    return content


def get_movie_list(soup):
    movies, seen = [], set()
    for tile in soup.select('.discovery-tiles__wrap .flex-container'):
        title = tile.select_one('[data-qa="discovery-media-list-item-title"], .p--small')
        link = tile.select_one('a[href^="/m/"]')
        image = tile.select_one('rt-img, img')
        if not title or not link:
            continue
        url = urljoin(BASE_MOVIE_URL, link['href'])
        if url in seen:
            continue
        seen.add(url)
        movies.append({'name': title.get_text(' ', strip=True),
                       'movie_url': url,
                       'img_url': image.get('src', '') if image else ''})
    if not movies:
        raise RuntimeError('No movie tiles found; check for a blocked response or changed markup.')
    return movies


def _movie_schema(soup):
    def walk(value):
        if isinstance(value, dict):
            types = value.get('@type', [])
            if 'Movie' in (types if isinstance(types, list) else [types]):
                yield value
            for child in value.values():
                yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)
    for tag in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(tag.get_text())
        except ValueError:
            continue
        for movie in walk(data):
            return movie
    return {}


def add_movie_info(item):
    if not item.get('movie_url'):
        return item
    soup = BeautifulSoup(fetch(item['movie_url'], save_cache=False), 'html.parser')
    schema = _movie_schema(soup)
    info = {}
    for row in soup.select('.category-wrap'):
        label = row.select_one('[data-qa="item-label"], dt')
        values = row.select('[data-qa="item-value"]')
        if label:
            info[label.get_text(' ', strip=True).rstrip(':').lower()] = ', '.join(
                x.get_text(' ', strip=True) for x in values)
    synopsis = soup.select_one('[data-qa="synopsis-value"], [data-qa="movie-info-synopsis"]')
    if not schema and not synopsis and not info:
        raise RuntimeError(f"No movie details found at {item['movie_url']}")
    genres = schema.get('genre', [])
    if isinstance(genres, str):
        genres = [genres]
    genre = info.get('genre') or ', '.join(genres)
    duration = info.get('runtime', '')
    item['meta'] = ', '.join(x for x in [genre, duration] if x)
    # JSON-LD description is currently SEO copy, not the actual synopsis.
    item['summary'] = synopsis.get_text(' ', strip=True) if synopsis else ''
    directors = schema.get('director', [])
    if isinstance(directors, dict):
        directors = [directors]
    item['director'] = info.get('director') or ', '.join(
        x['name'] for x in directors if isinstance(x, dict) and x.get('name'))
    item['starring'] = []
    for card in soup.select('.cast-and-crew [data-qa="person-item"], .cast-and-crew-item'):
        role = card.select_one('[data-qa="person-role"]')
        if role and role.get_text(' ', strip=True).casefold() in {
            'director', 'producer', 'executive producer', 'screenwriter',
            'writer', 'composer', 'cinematographer', 'editor',
        }:
            continue
        actor = card.select_one('[data-qa="person-name"], [data-qa="cast-crew-item-link"], p')
        if actor:
            name = actor.get_text(' ', strip=True)
            if name and name not in item['starring']:
                item['starring'].append(name)
        if len(item['starring']) == 2:
            break
    return item


def render(item, outfile, max_summary_len=MAX_SUMMARY_LEN):
    out = 'No new movies today.'
    if item.get('name'):
        out = r'\textbf{' + unicode_to_latex(item['name']) + '}'
        if item.get('meta'):
            out += ' ({})'.format(unicode_to_latex(item['meta']))
        if item.get('summary'):
            summary = item['summary']
            if len(summary) > max_summary_len:
                summary = summary[:max_summary_len].rsplit(' ', 1)[0] + '...'
            out += ': ' + unicode_to_latex(summary)
        if item.get('director'):
            out += ' Directed by ' + unicode_to_latex(item['director']) + '.'
        if item.get('starring'):
            out += ' Starring ' + unicode_to_latex(', '.join(item['starring'])) + '.'
    path = pathlib.Path(outfile)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(out, encoding='utf-8')
    return out


def main(outdir=CACHE_DIR, cached=True):
    movie_list = None
    if cached and is_cached():
        try:
            movie_list = get_movie_list(BeautifulSoup(load_cached(), 'html.parser'))
        except (RuntimeError, ValueError, OSError):
            pass
    if movie_list is None:
        movie_list = get_movie_list(BeautifulSoup(fetch(), 'html.parser'))
    movie = add_movie_info(pick_movie(movie_list))
    render(movie, os.path.join(outdir, 'movie.tex'))
    if movie and not cached:
        update_history(movie)


if __name__ == '__main__':
    main(cached=True)
