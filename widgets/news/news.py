import sys
import os.path
import pathlib
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex

# add parent dir so we can import Scraper
CUR_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.abspath(os.path.join(CUR_DIR, '..')))
from base import Scraper

CACHE_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'cache'))
BASE_URLS = {'sports': 'https://apnews.com/sports', 'music': 'https://pitchfork.com/reviews/best/albums/'}

MAX_HEADLINES = 3

class PitchforkReview(Scraper):
	def is_new(self, item):
		today = datetime.now() - timedelta(days=1)
		dtstr = item.select('.pub-date')[0].text
		dt = datetime.strptime(dtstr, '%B %d %Y')
		return dt.year == today.year and dt.month == today.month and dt.day == today.day

	def get(self):
		item = self.soup.select('.review')[0]
		if not self.is_new(item):
			return {}
		artist = item.select('.review__title-artist')[0].text.strip()
		album = item.select('.review__title-album')[0].text.strip()
		genre = item.select('.genre-list__item')[0].text.strip()
		url = 'https://pitchfork.com' + item.find('a').attrs['href']

		content = self.fetch(url)
		soup = self.parse(content)
		summary = soup.select('.grid--item')[3].text.strip()
		review = {'artist': artist, 'album': album, 'genre': genre, 'url': url, 'summary': summary}
		return review

	def render(self, item, outfile):
		out = ''
		if item:
			out += "\\textbf{Pitchfork's Best New Album}: "
			out += '\\textit{' + unicode_to_latex(item.get('album', '')) + '}'
			out += ' by ' + unicode_to_latex(item.get('artist', ''))
			out += ' [' + unicode_to_latex(item.get('genre', '')) + ']'
			out += ': ' + unicode_to_latex(item.get('summary', ''))
		with open(outfile, 'w') as f:
			f.write(out)

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
	main(name='sports')
	main(name='music')
