import sys
import os.path
import pathlib
from pylatexenc.latexencode import unicode_to_latex

# add parent dir so we can import Scraper
CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.abspath(os.path.join(CUR_DIR, '..')))
from base import Scraper

CACHE_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'cache'))
BASE_URLS = {'sports': 'https://apnews.com/sports'}

MAX_HEADLINES = 3

def get_headlines(soup, max_count=MAX_HEADLINES):
	headlines = []
	for item in soup.find('main').select('.PageList-items-item')[:max_count]:
		headline = [x.strip() for x in item.text.split('\n') if x][0]
		headlines.append(unicode_to_latex(headline))
	return headlines

def render_headlines(headlines):
	out = '\\begin{enumerate}\n'
	out += '\n'.join(['\\item ' + line for line in headlines])
	out += '\\end{enumerate}'
	return out

def render(headlines, outfile):
	with open(outfile, 'w') as f:
		out = render_headlines(headlines)
		f.write(out)

def main(name, cached=True, outdir=CACHE_DIR):
	sc = Scraper(url=BASE_URLS[name], cache_file='sports-news', try_cache=cached)
	headlines = get_headlines(sc.soup)
	outfile = os.path.join(outdir, '{}-news.tex'.format(name))
	render(headlines, outfile)

if __name__ == '__main__':
	main(name='sports')
