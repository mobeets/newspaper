import json
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime

import os.path
import pathlib
CURDIR = pathlib.Path(__file__).parent.resolve()

import matplotlib as mpl
mpl.rcParams['font.size'] = 14
mpl.rcParams['figure.figsize'] = [3.0, 3.0]
mpl.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'Helvetica'
# mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

CACHE_PATH = os.path.join(CURDIR, 'cache/forecast.json')
BASE_URL = 'https://api.weather.gov/points/{lat},{lon}'
locs = {'Somerville, MA': [42.39, -71.0868]}

def dtstr_to_dt(dtstr):
	return datetime.strptime(dtstr[:13], '%Y-%M-%dT%H')

def plot(rows, outfile=None):
	plt.figure(figsize=(4,2))
	xs = np.array([row['dt'].hour for row in rows])
	ys1 = np.array([row['temp'] for row in rows])
	ys2 = 100*np.array([row['precip'] for row in rows])
	ix = np.argsort(xs)

	color = 'blue'
	plt.plot(xs[ix], ys1[ix], label='temp', color=color)
	plt.xlabel('hour')
	plt.ylabel('temp. (F)', color=color)
	plt.xticks(ticks=xs[ix][::2].astype(int), rotation=90)

	ax2 = plt.gca().twinx()
	color = 'orange'
	ax2.plot(xs[ix], ys2[ix], color=color, label='precip')
	ax2.set_ylabel('precip. (%)', color=color)
	ax2.set_ylim([-2, 100])
	plt.tight_layout()
	plt.title("Today's forecast")

	if outfile is not None:
		plt.savefig(outfile)
	plt.close()

def is_same_day(dt1, dt2):
	return dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day

def get_time_series(out):
	today = datetime.now()
	rows = []
	for item in out['properties']['periods']:
		dt = dtstr_to_dt(item['startTime'])
		temp = item['temperature']
		prec = item['probabilityOfPrecipitation']['value']
		if is_same_day(today, dt):
			rows.append({'dt': dt, 'temp': temp, 'precip': prec})
	return rows

def load_cached():
	return json.load(open(CACHE_PATH))

def main(city, base_url=BASE_URL, cached=True, outfile=None):
	if cached:
		out = load_cached()
	else:
		lat, lon = locs[city]
		response = requests.get(base_url.format(lat=lat, lon=lon))
		out = response.json()
		forecast_url = out['properties']['forecastHourly']
		response = requests.get(forecast_url)
		out = response.json()
		json.dump(out, open(CACHE_PATH, 'w'))
	rows = get_time_series(out)
	plot(rows, outfile=outfile)

if __name__ == '__main__':
	main(city='Somerville, MA', cached=True, outfile=os.path.join(CURDIR, 'cache', 'forecast.png'))
