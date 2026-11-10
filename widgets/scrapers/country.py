"""Fetch a country, its flag, and two facts for the newspaper.

Place alongside base.py. Run from the newspaper project root:
    uv run python widgets/scrapers/country.py
Outputs: data/country.tex and data/flag.png
The parent LaTeX document must load graphicx.
"""
import hashlib
import io
import json
import pathlib
import random
from datetime import date

import requests
from PIL import Image
from pylatexenc.latexencode import unicode_to_latex
from base import CACHE_DIR

BASE_URL = 'https://www.apicountries.com/countries'
CACHE_PATH = pathlib.Path(CACHE_DIR) / 'country-of-day.json'


def fact_options(country):
    facts = []
    population = country.get('population')
    if type(population) is int and population > 0:
        facts.append(f'Population: {population:,}.')
    languages = list(dict.fromkeys(
        x['name'].strip() for x in country.get('languages', [])
        if isinstance(x, dict) and isinstance(x.get('name'), str) and x['name'].strip()
    ))
    if languages:
        label = 'Language' if len(languages) == 1 else 'Languages'
        facts.append(label + ': ' + ', '.join(languages) + '.')
    currencies = []
    for currency in country.get('currencies', []):
        if not isinstance(currency, dict) or not currency.get('name'):
            continue
        text = currency['name']
        if currency.get('code'):
            text += f" ({currency['code']})"
        if text not in currencies:
            currencies.append(text)
    if currencies:
        label = 'Currency' if len(currencies) == 1 else 'Currencies'
        facts.append(label + ': ' + ', '.join(currencies) + '.')
    return facts


def _valid_country(country):
    return (isinstance(country, dict) and isinstance(country.get('name'), str)
            and bool(country['name'].strip())
            and isinstance(country.get('flags'), dict)
            and isinstance(country['flags'].get('png'), str)
            and country['flags']['png'].startswith('https://')
            and len(fact_options(country)) >= 2)


def fetch():
    response = requests.get(BASE_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError('Countries API did not return a country list.')
    # This catalog also includes territories. Pick independent countries only.
    candidates = [c for c in data if _valid_country(c) and c.get('independent') is True]
    if not candidates:
        raise ValueError('Countries API returned no usable independent countries.')
    country = random.choice(candidates)
    return {'country': country, 'facts': random.sample(fact_options(country), 2)}


def get_country(cached=True, cache_path=CACHE_PATH):
    path = pathlib.Path(cache_path)
    today = date.today().isoformat()
    if cached and path.exists():
        try:
            item = json.loads(path.read_text(encoding='utf-8'))
            if (isinstance(item, dict) and item.get('date') == today
                    and _valid_country(item.get('country'))):
                options = fact_options(item['country'])
                facts = item.get('facts')
                if (isinstance(facts, list) and len(facts) == 2
                        and all(isinstance(fact, str) and fact in options for fact in facts)
                        and facts[0] != facts[1]):
                    return item
                # Upgrade today's old one-fact cache without changing countries.
                first = item.pop('fact', None)
                if first in options:
                    item['facts'] = [first, random.choice([f for f in options if f != first])]
                else:
                    item['facts'] = random.sample(options, 2)
                path.write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
                return item
        except (OSError, ValueError, TypeError, KeyError):
            pass
    item = dict(fetch(), date=today)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
    return item


def _as_png(binary):
    with Image.open(io.BytesIO(binary)) as image:
        image.load()
        output = io.BytesIO()
        image.convert('RGBA').save(output, format='PNG')
        return output.getvalue()


def get_flag(country):
    url = country['flags']['png']
    # Key flag caches by URL, so a changed API flag URL gets a fresh download.
    key = hashlib.sha256(url.encode('utf-8')).hexdigest()
    path = pathlib.Path(CACHE_DIR) / 'country-flags' / (key + '.png')
    if path.exists():
        try:
            return _as_png(path.read_bytes())
        except (OSError, ValueError):
            pass
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    binary = _as_png(response.content)  # Reject HTML/error pages, even HTTP 200.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(binary)
    return binary


def render(item, flag_path):
    country = item['country']
    # Paths resolve relative to the LaTeX process's working directory, just as
    # data/country.tex does. Absolute outdir paths also work.
    flag_path = pathlib.Path(flag_path).as_posix()
    if any(c in flag_path for c in '{}\n\r'):
        raise ValueError('The flag path contains characters unsupported by this LaTeX fragment.')
    return (r'\noindent\begin{minipage}[c]{0.24\linewidth}' + '\n'
            + r'\includegraphics[width=\linewidth,height=1cm,keepaspectratio]'
            + r'{\detokenize{' + flag_path + '}}\n'
            + r'\end{minipage}\hfill%' + '\n'
            + r'\begin{minipage}[c]{0.72\linewidth}\raggedright' + '\n'
            + r'\textbf{' + unicode_to_latex(country['name']) + r'}\par' + '\n'
            + '\n'.join(unicode_to_latex(fact) + r'\par' for fact in item['facts']) + '\n'
            + r'\end{minipage}\par' + '\n')


def main(cached=True, outdir='data'):
    item = get_country(cached=cached)
    outdir = pathlib.Path(outdir)
    flag_path = outdir / 'flag.png'
    tex_path = outdir / 'country.tex'
    # Prepare both outputs before overwriting either existing file.
    binary = get_flag(item['country'])
    content = render(item, flag_path)
    outdir.mkdir(parents=True, exist_ok=True)
    flag_path.write_bytes(binary)
    tex_path.write_text(content, encoding='utf-8')
    print(f"Country: {item['country']['name']}")
    print(f'Saved country to: {tex_path.resolve()}')
    print(f'Saved flag to: {flag_path.resolve()}')
    return str(tex_path.resolve())


if __name__ == '__main__':
    main(cached=True)
