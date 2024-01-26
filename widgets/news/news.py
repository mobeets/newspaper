import sys
import os.path
import pathlib

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
		headlines.append(headline)
	return headlines

def render(headlines, outfile):
	with open(outfile, 'w') as f:
		out = '\n\n\\noindent '.join(headlines)
		f.write(out)

def main(name, cached=True, outdir=CACHE_DIR):
	sc = Scraper(url=BASE_URLS[name], cache_file='sports-news', try_cache=cached)
	headlines = get_headlines(sc.soup)
	outfile = os.path.join(outdir, '{}-news.tex'.format(name))
	render(headlines, outfile)

if __name__ == '__main__':
	main()
