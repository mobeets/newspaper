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

CACHE_PATH = os.path.join(CURDIR, 'cache/weather.json')
BASE_URL = 'https://api.weather.gov/points/{lat},{lon}'
COORDINATES = {
	'Somerville': [42.39, -71.0868],
	'Pittsburgh': [40.4406, -79.9959],
	'Dallas': [32.9884109, -96.844696],
	'Houston': [29.7604, -95.3698],
	'Austin': [30.2672, -97.7431],
	}

def plot_time_series(rows, outfile=None):
	plt.figure(figsize=(4,2))
	xs = np.array([row['dt'].hour for row in rows])
	ys1 = np.array([row['temp'] for row in rows])
	ys2 = 100*np.array([row['precip'] for row in rows])
	ix = np.argsort(xs)

	color = 'blue'
	lnstl = '-'
	plt.plot(xs[ix], ys1[ix], lnstl, label='temp', color=color)
	plt.xlabel('hour')
	plt.ylabel('temp. (F)', color=color)
	plt.xticks(ticks=xs[ix][::2].astype(int), rotation=90)
	yticks = np.linspace(ys1[ix].min(), ys1[ix].max(), 4).astype(int)
	plt.yticks(ticks=yticks)

	ax2 = plt.gca().twinx()
	color = 'orange'
	lnstl = '--'
	ax2.plot(xs[ix], ys2[ix], lnstl, color=color, label='precip')
	ax2.set_ylabel('precip. (%)', color=color)
	ax2.set_ylim([-2, 102])
	plt.tight_layout()
	plt.title("Today's forecast")

	if outfile is not None:
		plt.savefig(outfile)
	plt.close()

def plot_stats_inner(stats, outfile=None):
	plt.figure(figsize=(3,2))
	xs = []
	ymin = 100
	ymax = 0
	for i, (city, stat) in enumerate(stats.items()):
		plt.plot(i*np.ones(2), [stat['low'], stat['high']], 'k-')
		plt.plot(i, stat['mean'], 'ko', markersize=4)
		xs.append(city)
		if stat['low'] < ymin:
			ymin = stat['low']
		if stat['high'] > ymax:
			ymax = stat['high']
	plt.xticks(ticks=range(len(stats)), labels=xs, rotation=90, fontsize=10)
	yticks = np.linspace(ymin, ymax, 4).astype(int)
	plt.yticks(yticks)
	plt.gca().axes.spines.right.set_visible(False)
	plt.tight_layout()
	if outfile is not None:
		plt.savefig(outfile)
	plt.close()

def is_same_day(dt1, dt2):
	return dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day

def dtstr_to_dt(dtstr):
	return datetime.strptime(dtstr[:13], '%Y-%M-%dT%H')

def get_time_series(forecast):
	today = datetime.now()
	rows = []
	for item in forecast['properties']['periods']:
		dt = dtstr_to_dt(item['startTime'])
		temp = item['temperature']
		prec = item['probabilityOfPrecipitation']['value']
		if is_same_day(today, dt):
			rows.append({'dt': dt, 'temp': temp, 'precip': prec})
	return rows

def get_stats(rows):
	low = 100
	high = -100
	temps = []
	for row in rows:
		if row['temp'] < low:
			low = row['temp']
		elif row['temp'] > high:
			high = row['temp']
		temps.append(row['temp'])
	return {'low': low, 'high': high, 'mean': np.mean(temps)}

def plot_stats(weather, outfile=None):
	stats = {}
	for city in weather:
		stats[city] = get_stats(get_time_series(weather[city]['forecast']))
	plot_stats_inner(stats, outfile=outfile)

def load_cached_weather():
	return json.load(open(CACHE_PATH))

def fetch_weather(cities=None, base_url=BASE_URL, cachepath=CACHE_PATH):
	cache = {}
	if cities is None:
		cities = list(COORDINATES.keys())
	for city in cities:
		lat, lon = COORDINATES[city]
		response = requests.get(base_url.format(lat=lat, lon=lon))
		out1 = response.json()
		forecast_url = out1['properties']['forecastHourly']
		response = requests.get(forecast_url)
		out2 = response.json()
		cache[city] = {'response': out1, 'forecast': out2}
	json.dump(cache, open(CACHE_PATH, 'w'))
	return cache

def main(city='Somerville', outdir=None, cached=True):
	if outdir is None:
		outdir = os.path.join(CURDIR, 'cache')
	
	fnm1 = os.path.join(outdir, 'weather-forecast.png')
	fnm2 = os.path.join(outdir, 'weather-ranges.png')

	weather = load_cached_weather() if cached else fetch_weather()

	plot_time_series(get_time_series(weather[city]['forecast']),
		outfile=os.path.join(outdir, 'weather-forecast.png'))
	plot_stats(weather, outfile=os.path.join(outdir, 'weather-ranges.png'))

if __name__ == '__main__':
	main(cached=True)
