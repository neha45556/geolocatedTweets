#!/usr/bin/env python3

import tweepy
import json
import time
import threading
import copy
import re
import requests
import lxml.html
import sys
import os

import queue
#heads up: this takes a long time if your gonna do the full 2GB, it already takes a long time just for 5KB

# Data directory.
data_directory='data'
# Desired file size in bytes.
max_file_size=5000
# Average tweet size in bytes.
avg_tweet_size=200
# Tweets per file; if nonzero, above 2 options are ignored.
tweets_per_file=0
# Interval to write data to disk.
dump_interval_secs=10

##
# Function crawl_url
#
# Parameters: url (string) (URL to visit)
# Returns: title of page (string)
# Returns none if page does not exist, errors, or is not HTML text.
def crawl_url(url):
	retdata = None
	try:
		r = requests.get(url)
		if r.status_code != 200: # HTTP OK
			raise requests.exceptions.RequestException('Non-success return code')
		if r.headers['content-type'][:9] != 'text/html':
			raise requests.exceptions.RequestException('Non-HTML data')

		tree = lxml.html.fromstring(r.content)
		retdata = tree.findtext('.//title')
	except requests.exceptions.RequestException:
		return None
	except lxml.etree.XMLSyntaxError:
		return None

	return retdata or None

##
# Class TweetData
#
# Queues data from a Twitter stream, parses it, and saves it
# to disk. Thread-safe.
#
# Paramters: filesize (desired file size in bytes),
#            tweetsize (estimated storage size per tweet, in bytes)
#            tweetsperfile (number of tweets per file; overrides filesize and 
#                          tweetsize if nonzero)
#
# Functions:
#            append: Queue data for parsing and crawling.
#                    Takes a dictionary with keys user (string),
#                    text (string), links (empty array), location (array).
#
#            parse: Parse all data queued by `append`.
#
#            dump: Save data to disk parsed by `parse`.
class TweetData:
	def __init__(self, data_directory='.', filesize=10000000, tweetsize=450, tweetsperfile=0):
		if data_directory != '.':
			if not os.path.isdir(data_directory):
				try:
					os.mkdir(data_directory)
				except OSError:
					print("Directory creation failed; make sure it doesn't exist already and you have write permissions to the file system.")
					sys.exit()

		current_files = os.listdir(data_directory)
		self._file_counter = 1
		for filename in current_files:
			match = re.match(r'^([0-9]+)\.json$', filename)
			if match:
				matchnum = int(match.group(1))
				if self._file_counter <= matchnum:
					self._file_counter = matchnum + 1

		print(f'Starting at file {self._file_counter}')
		self._tweets_per_file = tweetsperfile or (filesize / tweetsize)
		self._parsed_data_lock = threading.Lock()
		self._unparsed_data = queue.Queue(maxsize=self._tweets_per_file)
		self._data = []
		self._thread_count = 16
		self._threads = []

		for i in range(self._thread_count):
			t = threading.Thread(target=self.parse)
			t.daemon = True
			t.start()
			self._threads.append(t)
			
		print(f'Spawned {len(self._threads)} getter threads')

	def __len__(self):
		return len(self._data)

	def append(self, data):
		queue_size = self._unparsed_data.qsize()
		if queue_size > 0:
			print("queue size: " + str(queue_size))
		if len(data['links']) > 0: # Only queue items that have urls to get.
			try:
				self._unparsed_data.put_nowait(data)
			except queue.Full:
				with self._parsed_data_lock:
					print("Warning: queue is full; skipping 1 entry.");
					self._data.append(data);
		else:
			self._data.append(data);

	def parse(self):
		worker_has_work = True;
		while worker_has_work:
			entry = self._unparsed_data.get()
			# Parse for URLs here
			for link in entry['links']:
				page_title = crawl_url(link['url'])
				if page_title:
					link['title'] = page_title
			with self._parsed_data_lock:
				self._data.append(entry)
			self._unparsed_data.task_done()

	# TODO: Run parser asynchronously.
	def dump(self):
		cnt = self._file_counter
		with self._parsed_data_lock:
			tmp = []
			tmp.extend(self._data)
			if (len(tmp) > self._tweets_per_file):
				self._file_counter += 1
				self._data.clear()
		with open(f'{data_directory}/{cnt}.json', 'w') as f:
			print(json.dumps(tmp), file=f)

class MyStreamListener(tweepy.StreamListener):
	def set_datastore(self, datastore):
		self._datastore = datastore

	def on_status(self,tweet):
		#print(f"Recv tweet: {tweet.text[:12]}...")
		self._datastore.append({
			"user" : tweet.user.name or '',
			"text" : tweet.text or '',
			"links" : [{'url' : url['expanded_url'], 'title' : None} for url in tweet.entities['urls']],
			"location" : dict(tweet.coordinates or {})
			})
		return True

	def on_error(self, status):
		print(f"Error:{status}")

if __name__ == "__main__":
	conf = None
	locations_to_track = [-119.859391, 33.013882, -115.904313, 34.884276]
	with open('config.json', 'r') as conf_raw:
		conf = json.load(conf_raw)
		max_file_size = conf["desired file size (bytes)"]
		avg_tweet_size = conf["estimated size of tweet (bytes)"]
		tweets_per_file = conf["number of tweets per file (if non-zero, filesize and tweet size are ignored)"]
		dump_interval_secs = conf["interval to flush data to disk (seconds)"]
		locations_to_track = conf["bounding boxes to track (degrees east, degrees north; southeast, northwest)"]
		data_directory = conf["data directory"]

	auth = tweepy.OAuthHandler("E0b6PlhPOGqJtqeKTRda74SLS", "3iLsGyLf95lQPFbzWGDhjLtLuGBO5CG2TEMhniqwFrqsFJBXMe")
	auth.set_access_token("3500144893-zpXqTRLyBAEmClgbC1RUDGX1ggyQ901a4OTHVUr",
						  "GaVhSEpGxctyIY4zBn11tSNJNMt72naUjB1BhNT51iV0V")
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	tweets_listener = MyStreamListener(api)
	tweets_datastore = TweetData(data_directory=data_directory, filesize=max_file_size, tweetsize=avg_tweet_size, tweetsperfile=tweets_per_file)
	tweets_listener.set_datastore(tweets_datastore)
	stream = tweepy.Stream(api.auth, tweets_listener)

	# TODO: pick version to use more smartly. This is jank af.
	try:
		print(f"Tweepy version {tweepy.__version__}");
		stream.filter(locations=locations_to_track, async=True)
	except TypeError:
		print(f"Tweepy version {tweepy.__version__}, falling back to `is_async`");
		stream.filter(locations=locations_to_track, is_async=True)

	while 1:
		try:
			tweets_datastore.dump()
			time.sleep(dump_interval_secs)
		except KeyboardInterrupt:
			tweets_datastore.dump()
			sys.exit()
			
