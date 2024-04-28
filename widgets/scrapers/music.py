import sys
import os.path
import pathlib
from datetime import datetime, timedelta
from pylatexenc.latexencode import unicode_to_latex, UnicodeToLatexEncoder
from base import Scraper, CACHE_DIR

u = UnicodeToLatexEncoder(unknown_char_policy='ignore')
unicode_to_latex = lambda x: u.unicode_to_latex(x)

BASE_URLS = {'music': 'https://pitchfork.com/reviews/best/albums/'}

class PitchforkReview(Scraper):
	def is_new(self, item):
		today = datetime.now() - timedelta(days=1)
		# dtstr = item.select('.pub-date')[0].text
		# dt = datetime.strptime(dtstr, '%B %d %Y')
		dtstr = item.select('time')[0].text
		dt = datetime.strptime(dtstr, '%B %d, %Y')
		return dt.year == today.year and dt.month == today.month and dt.day == today.day

	def get(self):
		# item = self.soup.select('.review')[0]
		item = self.soup.select('.summary-item')[0]
		if not self.is_new(item):
			return {}
		
		# artist = item.select('.review__title-artist')[0].text.strip()
		# album = item.select('.review__title-album')[0].text.strip()
		# genre = item.select('.genre-list__item')[0].text.strip()

		artist = item.select('.summary-item__sub-hed')[0].text.strip()
		album = item.select('.summary-item__hed')[0].text.strip()
		genre = genre = item.select('.summary-item__rubric')[0].text.strip()
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
		if outfile is not None:
			with open(outfile, 'w') as f:
				f.write(out)
		else:
			print(out)

def main(name='music', cached=True, outdir=CACHE_DIR):
	outfile = os.path.join(outdir, '{}-news.tex'.format(name))
	sc = PitchforkReview(url=BASE_URLS[name], cache_file='{}-news'.format(name), try_cache=cached)
	review = sc.get()
	outfile = sc.render(review, outfile)

if __name__ == '__main__':
	main(cached=True)
