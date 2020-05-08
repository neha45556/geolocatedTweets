#variables that contain the user credentials to access Twitter API

import tweepy
import json
import os,sys
import time
#import io	#gives backward compatibility with python 2 (NOT NEEDED)
# from tweepy.streaming import StreamListener
# from tweepy import OAuthHandler
# from tweepy import Stream


#heads up: this takes a long time if your gonna do the full 2GB, it already takes a long time just for 5KB


#this is for one file size, we need separate files of 10MB all adding up to 2GB
#for testing it might be faster to make separate files of 1KB up to 5KB
max_file_size=5000		#Replace this with 2000000000 for 2GB bytes, can use 5000 for 5KB for testing
avg_tweet_size=200
dump_interval_secs=10
counter = 1
open('testfile.json', 'w+', encoding="utf-8").close() 	#empties the file and also creates the file if it doesnt exist

# TODO: Add thread-safety
tweet_data = []

def dump_data(filename):
	with open(filename, 'w') as f:
		print(json.dumps(tweet_data), file=f);
	

class MyStreamListener(tweepy.StreamListener):

	
	def _init_(self, e):
		self.max_file_size = 20
		self.cntr = 1

	def on_status(self,tweet):
		tweet_data.append({
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
	stream = tweepy.Stream(api.auth, tweets_listener)
	stream.filter(locations=[-119.859391, 33.013882, -115.904313, 34.884276], async=True)
	while 1:
		print(f"Dumping data into file number {counter}...");
		dump_data(f"{counter}.json");
		if len(tweet_data) >= max_file_size / avg_tweet_size:
			counter += 1;
			tweet_data.clear();
			
		time.sleep(dump_interval_secs);
