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

import urlre

#heads up: this takes a long time if your gonna do the full 2GB, it already takes a long time just for 5KB

# Desired file size in bytes.
max_file_size=5000
# Average tweet size in bytes.
avg_tweet_size=200
# Interval to write data to disk.
dump_interval_secs=10

##
# Function crawl_url
#
# Parameters: url (string) (URL to visit)
# Returns: Tuple(url, title of page)
# Returns none if page does not exist, errors, or is not HTML text.
def crawl_url(url):
	retdata = {}
	try:
		r = requests.get(url)
		if r.status_code != 200: # HTTP OK
			raise requests.exceptions.RequestException('Non-success return code')
		if r.headers['content-type'][:9] != 'text/html':
			raise requests.exceptions.RequestException('Non-HTML data')

		tree = lxml.html.fromstring(r.content)
		title = tree.findtext('.//title')
		if title:
			retdata = { 'url' : r.url, 'title' : title }
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
	def __init__(self, filesize=10000000, tweetsize=250):
		self._tweetsperfile = filesize / tweetsize
		self._unparsed_data_lock = threading.Lock()
		self._parsed_data_lock = threading.Lock()
		self._file_counter = 1
		self._unparsed_data = []
		self._data = []

	def __len__(self):
		return len(self._data)

	def append(self, data):
		print("append: " + str(len(self._unparsed_data)))
		# TODO: Pick overflow number at runtime.
		needs_flush = False;
		with self._unparsed_data_lock:
			if len(self._unparsed_data) > 250:
				print("Warning: Parsing/crawling is falling behind!");
				print(f"Warning: Skipping parsing of {len(self._unparsed_data)} entries.");
				needs_flush = True
			self._unparsed_data.append(data)
		if needs_flush:
			with self._parsed_data_lock:
				self._data.extend(self._unparsed_data)
				self._unparsed_data.clear()

	def parse(self):
		pos = len(self._data)
		parse_buffer = []
		with self._unparsed_data_lock:
			parse_buffer.extend(self._unparsed_data)
			self._unparsed_data.clear()
			print("parse: " + str(len(self._data)))
		for i in range(len(parse_buffer)):
			# Parse for URLs here
			url_matches = re.findall(urlre.url, parse_buffer[i]['text'])
			for url in url_matches:
				crawled_data = crawl_url(url)
				if crawled_data:
					parse_buffer[i]['links'].append(crawl_url(url))
		if parse_buffer:
			with self._parsed_data_lock:
				self._data.extend(parse_buffer)

	def dump(self):
		self.parse()
		with self._parsed_data_lock:
			tmp = copy.deepcopy(self._data)
			if (len(tmp) > self._tweetsperfile):
				self._file_counter += 1
				self._data.clear()
		with open(f'{self._file_counter}.json', 'w') as f:
			print(json.dumps(tmp), file=f)

class MyStreamListener(tweepy.StreamListener):
	def set_datastore(self, datastore):
		self._datastore = datastore

	def on_status(self,tweet):
		#print(f"Recv tweet: {tweet.text[:12]}...")
		self._datastore.append({
			"user" : tweet.user.name or '',
			"text" : tweet.text or '',
			"links" : [],
			"location" : [] })
		return True

	def on_error(self, status):
		print("Error:{status}")

if __name__ == "__main__":
	auth = tweepy.OAuthHandler("E0b6PlhPOGqJtqeKTRda74SLS", "3iLsGyLf95lQPFbzWGDhjLtLuGBO5CG2TEMhniqwFrqsFJBXMe")
	auth.set_access_token("3500144893-zpXqTRLyBAEmClgbC1RUDGX1ggyQ901a4OTHVUr",
						  "GaVhSEpGxctyIY4zBn11tSNJNMt72naUjB1BhNT51iV0V")
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	tweets_listener = MyStreamListener(api)
	tweets_datastore = TweetData(filesize=max_file_size, tweetsize=avg_tweet_size)
	tweets_listener.set_datastore(tweets_datastore)
	stream = tweepy.Stream(api.auth, tweets_listener)

	try:
		print(f"Tweepy version {tweepy.__version__}");
		stream.filter(locations=[-119.859391, 33.013882, -115.904313, 34.884276], async=True)
	except TypeError:
		print(f"Tweepy version {tweepy.__version__}, falling back to `is_async`");
		stream.filter(locations=[-119.859391, 33.013882, -115.904313, 34.884276], is_async=True)

	while 1:
		try:
			tweets_datastore.dump()
			time.sleep(dump_interval_secs)
		except KeyboardInterrupt:
			tweets_datastore.dump()
			sys.exit()
			
