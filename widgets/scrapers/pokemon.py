import hashlib
import json
import pathlib
import random
from datetime import datetime

import requests
from pylatexenc.latexencode import UnicodeToLatexEncoder
from base import CACHE_DIR

BASE_URL = 'https://pokeapi.co/api/v2'
N_POKEMON = 1025


class Pokedex:
    # Keep the original constructor/main call pattern, but fetch JSON directly:
    # Scraper.__init__ expects HTML, so this class no longer inherits from it.
    def __init__(self, base_url=BASE_URL, try_cache=True, cache_file='pokedex'):
        self.base_url = base_url.rstrip('/')
        self.try_cache = try_cache
        self.cache_dir = pathlib.Path(CACHE_DIR) / (cache_file + '-pokeapi')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self._responses = {}

        inds = list(range(1, N_POKEMON + 1))
        random.Random(666).shuffle(inds)
        day_index = (datetime.today().date() - datetime(2024, 1, 27).date()).days
        self.poke_index = inds[day_index % len(inds)]

    def _get_json(self, url):
        if url in self._responses:
            return self._responses[url]
        key = hashlib.sha256(url.encode('utf-8')).hexdigest()
        cache_path = self.cache_dir / (key + '.json')
        data = None
        if self.try_cache and cache_path.exists():
            try:
                data = json.loads(cache_path.read_text(encoding='utf-8'))
            except (ValueError, OSError):
                pass
        if data is None:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        self._responses[url] = data
        return data

    @staticmethod
    def _english_name(species):
        return next(
            (entry['name'] for entry in species['names']
             if entry['language']['name'] == 'en'),
            species['name'].replace('-', ' ').title(),
        )

    def get(self):
        species = self._get_json(
            f'{self.base_url}/pokemon-species/{self.poke_index}/'
        )
        # Species IDs and default variety IDs need not be identical.
        variety = next(v for v in species['varieties'] if v['is_default'])
        pokemon = self._get_json(variety['pokemon']['url'])
        name = self._english_name(species)

        descriptions = [entry['flavor_text']
                        for entry in species['flavor_text_entries']
                        if entry['language']['name'] == 'en']
        desc = ' '.join(descriptions[-1].split()) if descriptions else ''
        sprites = pokemon['sprites']
        img_url = (
            sprites.get('other', {}).get('official-artwork', {}).get('front_default')
            or sprites['front_default']
        )
        if not img_url:
            raise RuntimeError(f'No image available for {name}')
        kind = ' / '.join(entry['type']['name'].title()
                          for entry in sorted(pokemon['types'], key=lambda x: x['slot']))

        # Represent each branch separately (e.g. Eevee's evolutions).
        # Flattening the tree and joining with arrows would imply false chains.
        paths = []
        evolution_chain = species.get('evolution_chain')
        if evolution_chain:
            chain = self._get_json(evolution_chain['url'])['chain']

            def visit(node, path):
                ref = node['species']
                if ref['name'] == species['name']:
                    node_name = name
                else:
                    node_name = self._english_name(self._get_json(ref['url']))
                path = path + [node_name]
                if node['evolves_to']:
                    for child in node['evolves_to']:
                        visit(child, path)
                else:
                    paths.append(path)

            visit(chain, [])
        paths = [path for path in paths if len(path) > 1]
        evols = list(dict.fromkeys(n for path in paths for n in path))
        return {'name': name, 'desc': desc, 'index': self.poke_index,
                'img_url': img_url, 'kind': kind, 'evols': evols,
                'evolution_paths': paths}

    def fetch_and_save_image(self, url, outfile):
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        outfile = pathlib.Path(outfile)
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_bytes(response.content)

    def render(self, item, outfile):
        encoder = UnicodeToLatexEncoder(unknown_char_policy='replace')

        def tex(value):
            return encoder.unicode_to_latex(str(value))

        out = ('Pokémon of the day:\n\\textbf{' + tex(item['name']) + '}'
               + r' (\#' + tex(item['index']) + ')'
               + ' [' + tex(item['kind']) + '].')
        out += '\n' + tex(item['desc'])
        paths = item.get('evolution_paths', [])
        if paths:
            out += '\nEvolutions: ' + '; '.join(
                r' $\rightarrow$ '.join(tex(name) for name in path)
                for path in paths
            )
        outfile = pathlib.Path(outfile)
        outfile.parent.mkdir(parents=True, exist_ok=True)
        outfile.write_text(out, encoding='utf-8')
        return out


def main(cached=True, outdir=CACHE_DIR, datadir=CACHE_DIR):
    sc = Pokedex(BASE_URL, try_cache=cached, cache_file='pokedex')
    outfile = pathlib.Path(datadir) / 'pokedex.tex'
    imgfile = pathlib.Path(outdir) / 'pokedex.png'
    pokemon = sc.get()
    sc.fetch_and_save_image(pokemon['img_url'], imgfile)
    print(sc.render(pokemon, outfile))


if __name__ == '__main__':
    main(cached=True)
