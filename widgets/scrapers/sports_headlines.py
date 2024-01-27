import sys
import os.path
import pathlib
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex
from base import Scraper, CACHE_DIR

BASE_URLS = {'sports': 'https://apnews.com/sports', 'music': 'https://pitchfork.com/reviews/best/albums/'}

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

def main(name='sports', cached=True, outdir=CACHE_DIR):
	outfile = os.path.join(outdir, '{}-news.tex'.format(name))
	if name == 'sports':
		sc = Scraper(url=BASE_URLS[name], cache_file='{}-news'.format(name), try_cache=cached)
		headlines = get_headlines(sc.soup)
		render(headlines, outfile)
	elif name == 'music':
		sc = PitchforkReview(url=BASE_URLS[name], cache_file='{}-news'.format(name), try_cache=cached)
		review = sc.get()
		outfile = sc.render(review, outfile)

if __name__ == '__main__':
	main()
