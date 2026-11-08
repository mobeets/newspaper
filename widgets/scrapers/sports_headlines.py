"""Render Basketball Reference's Yesterday's Top Performers as LaTeX.

Uses requests, beautifulsoup4, and pylatexenc; imports CACHE_DIR from base.py.
main(html_file='saved-homepage.html') can read a locally saved homepage.
"""
import json
import os.path
import pathlib
import re
from datetime import date

import requests
from bs4 import BeautifulSoup, Comment
from pylatexenc.latexencode import unicode_to_latex
from base import CACHE_DIR

BASE_URL = 'https://www.basketball-reference.com/'
BASE_URLS = {'sports': BASE_URL}
MAX_PERFORMERS = 5
MAX_HEADLINES = MAX_PERFORMERS


def _text(tag):
    return ' '.join(tag.get_text(' ', strip=True).split())


def _heading(text):
    return re.sub(r'[^a-z]', '', text.lower())


def get_performers(soup, max_count=MAX_PERFORMERS):
    if max_count <= 0:
        return []
    # Sports Reference sometimes places tables inside HTML comments.
    soup = BeautifulSoup(str(soup), 'html.parser')
    for comment in list(soup.find_all(string=lambda s: isinstance(s, Comment))):
        if '<table' in comment.lower():
            comment.replace_with(BeautifulSoup(str(comment), 'html.parser'))
    heading = next((tag for tag in soup.find_all(re.compile(r'^h[1-6]$'))
                    if _heading(_text(tag)) == 'yesterdaystopperformers'), None)
    if heading is None:
        raise RuntimeError("Basketball Reference's Yesterday's Top Performers section "
                           'was not found. The page may be blocked or its markup changed.')
    table = None
    for tag in heading.find_all_next():
        if tag.name == 'table':
            table = tag
            break
        if re.fullmatch(r'h[1-6]', tag.name or ''):
            break
    if table is None:
        raise RuntimeError('The Top Performers section does not contain a table. '
                           'There may have been no games, or the markup changed.')
    performers = []
    for row in table.select('tr'):
        player = row.select_one('a[href*="/players/"]')
        if player is None:
            continue
        cells = row.find_all(['th', 'td'], recursive=False)
        if not cells:
            continue
        team_link = row.select_one('a[href*="/teams/"]')
        player_cell = player.find_parent(['th', 'td'])
        team = _text(team_link).strip('() ') if team_link else ''
        if not team and player_cell:
            match = re.search(r'\(([^)]+)\)', _text(player_cell))
            team = match.group(1).strip() if match else ''
        by_stat = {cell.get('data-stat'): _text(cell) for cell in cells
                   if cell.get('data-stat')}
        # The homepage's displayed order is player, PTS, TRB, AST, GmSc.
        stats = []
        for index, aliases in enumerate((('pts',), ('trb',), ('ast',),
                                         ('game_score', 'gmsc')), start=1):
            value = next((by_stat[key] for key in aliases if key in by_stat), '')
            if not value and index < len(cells):
                value = _text(cells[index])
            stats.append(value)
        if any(not re.fullmatch(r'-?\d+(?:\.\d+)?', value) for value in stats):
            raise RuntimeError('A Top Performers row has missing or unrecognized statistics.')
        performers.append(dict(zip(('name', 'team', 'pts', 'trb', 'ast', 'gmsc'),
                                   [_text(player), team] + stats)))
        if len(performers) >= max_count:
            break
    if not performers:
        raise RuntimeError('No player rows found in the Top Performers table.')
    return performers


def get_headlines(soup, max_count=MAX_PERFORMERS):
    """Compatibility helper: return LaTeX list items in the site's order."""
    return [_format_player(player) for player in get_performers(soup, max_count)]


def _format_player(player):
    label = player['name'] + (f" ({player['team']})" if player['team'] else '')
    return (r'\textbf{' + unicode_to_latex(label) + '}: '
            + ', '.join(unicode_to_latex(str(player[key])) + ' ' + unit
                        for key, unit in [('pts', 'PTS'), ('trb', 'REB'),
                                          ('ast', 'AST'), ('gmsc', 'GmSc')]))


def render_headlines(headlines):
    if not headlines:
        return ''
    return (r"\textbf{Yesterday's Top Performers (NBA)}" + '\n'
            + '\\begin{enumerate}\n'
            + '\n'.join('\\item ' + line for line in headlines)
            + '\n\\end{enumerate}\n')


def render(headlines, outfile):
    path = pathlib.Path(outfile)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = render_headlines(headlines)
    path.write_text(out, encoding='utf-8')
    return out


def main(name='sports', cached=True, outdir=CACHE_DIR, html_file=None):
    if name != 'sports':
        raise ValueError("name must be 'sports'")
    cache_path = pathlib.Path(CACHE_DIR) / 'basketball-top-performers-v1.json'
    today = date.today().isoformat()
    performers = None
    if cached and html_file is None and cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding='utf-8'))
            if data['date'] == today and data['source'] == BASE_URL:
                candidate = data['performers']
                if not isinstance(candidate, list) or not candidate:
                    raise ValueError('Invalid cached performers')
                for player in candidate:
                    _format_player(player)
                performers = candidate[:MAX_PERFORMERS]
        except (OSError, ValueError, KeyError, TypeError):
            pass
    if performers is None:
        if html_file is not None:
            content = pathlib.Path(html_file).read_text(encoding='utf-8')
        else:
            response = requests.get(BASE_URL, timeout=30)
            if response.status_code == 403:
                raise RuntimeError('Basketball Reference returned HTTP 403 Forbidden. '
                                   'The site is rejecting this request; no package installation '
                                   'or parser change fixes that. You can save the homepage as '
                                   'HTML in your browser and call main(html_file="saved-page.html").')
            response.raise_for_status()
            content = response.content
        performers = get_performers(BeautifulSoup(content, 'html.parser'))
        # A saved page may be old; do not mark its data as today's live cache.
        if html_file is None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps({'date': today, 'source': BASE_URL,
                                             'performers': performers}, ensure_ascii=False),
                                  encoding='utf-8')
    return render([_format_player(p) for p in performers],
                  os.path.join(outdir, f'{name}-news.tex'))


if __name__ == '__main__':
    main()
