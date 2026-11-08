"""Fetch one dad joke and write it as a LaTeX fragment.

Run alongside base.py with: uv run python dadjoke.py
Output: os.path.join(CACHE_DIR, 'dadjoke.tex')
"""
import json
import pathlib
from datetime import date

import requests
from pylatexenc.latexencode import unicode_to_latex
from base import CACHE_DIR

BASE_URL = 'https://icanhazdadjoke.com/'
CACHE_PATH = pathlib.Path(CACHE_DIR) / 'dadjoke.json'
HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'newspaper-dadjoke-widget (personal newspaper project)',
}


def _validate(item):
    if (not isinstance(item, dict) or item.get('status') != 200
            or not isinstance(item.get('joke'), str) or not item['joke'].strip()):
        raise ValueError('The joke API did not return a valid joke.')
    return item


def fetch():
    response = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return _validate(response.json())


def get_joke(cached=True, cache_path=CACHE_PATH):
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
    joke = ' '.join(item['joke'].split())
    out = unicode_to_latex(joke) + '\n'
    outfile = pathlib.Path(outfile)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(out, encoding='utf-8')
    return out


def main(cached=True, outdir=CACHE_DIR):
    item = get_joke(cached=cached)
    outfile = pathlib.Path(outdir) / 'dadjoke.tex'
    render(item, outfile)
    saved_path = str(outfile.resolve())
    print(f'Saved joke to: {saved_path}')
    return saved_path


if __name__ == '__main__':
    main(cached=True)
