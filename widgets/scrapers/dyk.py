"""Fetch a random English fact and write data/dyk.tex.

Place alongside base.py. Run from the newspaper project root:
    uv run python widgets/scrapers/dyk.py
"""
import json
import pathlib
from datetime import date

import requests
from pylatexenc.latexencode import unicode_to_latex
from base import CACHE_DIR

BASE_URL = 'https://uselessfacts.jsph.pl/api/v2/facts/random'
CACHE_PATH = pathlib.Path(CACHE_DIR) / 'dyk.json'


def _validate(item):
    if (not isinstance(item, dict) or not isinstance(item.get('text'), str)
            or not item['text'].strip()):
        raise ValueError('The facts API did not return valid fact text.')
    return item


def fetch():
    response = requests.get(
        BASE_URL, params={'language': 'en'},
        headers={'Accept': 'application/json'}, timeout=30,
    )
    response.raise_for_status()
    return _validate(response.json())


def get_fact(cached=True, cache_path=CACHE_PATH):
    cache_path = pathlib.Path(cache_path)
    today = date.today().isoformat()
    if cached and cache_path.exists():
        try:
            item = _validate(json.loads(cache_path.read_text(encoding='utf-8')))
            if item.get('date') == today:
                return item
        except (OSError, ValueError):
            pass
    item = dict(fetch(), date=today)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
    return item


def render(item, outfile):
    _validate(item)
    text = ' '.join(item['text'].split())
    out = unicode_to_latex(text) + '\n'
    outfile = pathlib.Path(outfile)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(out, encoding='utf-8')
    return out


def main(cached=True, outdir='data'):
    item = get_fact(cached=cached)
    outfile = pathlib.Path(outdir) / 'dyk.tex'
    render(item, outfile)
    saved_path = str(outfile.resolve())
    print(f'Saved fact to: {saved_path}')
    return saved_path


if __name__ == '__main__':
    main(cached=True)
