#variables that contain the user credentials to access Twitter API

import tweepy
import json
import time
import threading
import copy

#heads up: this takes a long time if your gonna do the full 2GB, it already takes a long time just for 5KB
max_file_size=5000
avg_tweet_size=200
dump_interval_secs=10

class TweetData:
	def __init__(self, filesize=10000000, tweetsize=250):
		self._tweetsperfile = filesize / tweetsize
		self._data_lock = threading.Lock()
		self._file_counter = 1
		self._data = []

	def __len__(self):
		return len(self._data)

	def append(self, data):
		with self._data_lock:
			self._data.append(data)

	def dump(self):
		with self._data_lock:
			tmp = copy.copy(self._data)
		with open(f'{self._file_counter}.json', 'w') as f:
			print(json.dumps(tmp), file=f);
		if (len(tmp) > self._tweetsperfile):
			self._file_counter += 1;
			self._data.clear();
		
class MyStreamListener(tweepy.StreamListener):
	def set_datastore(self, datastore):
		self._datastore = datastore

	def on_status(self,tweet):
		self._datastore.append({
			"user" : tweet.user.name,
			"text" : tweet.text.replace('\\','\\\\').replace('"','\\"'),
			"links" : {},
			"location" : [] });
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
	stream.filter(locations=[-119.859391, 33.013882, -115.904313, 34.884276], async=True)
	while 1:
		tweets_datastore.dump();
		time.sleep(dump_interval_secs);
