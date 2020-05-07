#variables that contain the user credentials to access Twitter API

import tweepy
import json
# import os,sys
# from tweepy.streaming import StreamListener
# from tweepy import OAuthHandler
# from tweepy import Stream


class MyStreamListener(tweepy.StreamListener):

	def _init_(self, e):
		self.max_file_size = 10000000
		self.cntr = 1

	def create(self,tweet):
		cntr = 1
		max_file_size = 10000
		while (cntr < 10):
			with open(f'{cntr}.json', 'a') as json_file:  # cntr becomes new file name ?3
				if (os.stat(f'{cntr}.json').st_size < max_file_size):
					json_file.write(tweet.text)
					json_file.write('\n')
				# on_status(tweet)
				else:
					cntr = cntr + 1


	def on_status(self,tweet):
		print(tweet.text)
		#print(f"{tweet.user.name}:{tweet.text}")1
		self.create(tweet)

		return True

	def on_error(self, status):
		print(status)

if __name__ == "__main__":
	auth = tweepy.OAuthHandler("E0b6PlhPOGqJtqeKTRda74SLS", "3iLsGyLf95lQPFbzWGDhjLtLuGBO5CG2TEMhniqwFrqsFJBXMe")
	auth.set_access_token("3500144893-zpXqTRLyBAEmClgbC1RUDGX1ggyQ901a4OTHVUr",
						  "GaVhSEpGxctyIY4zBn11tSNJNMt72naUjB1BhNT51iV0V")
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	tweets_listener = MyStreamListener(api)
	stream = tweepy.Stream(api.auth, tweets_listener)
	stream.filter(locations=[-119.859391, 33.013882, -115.904313, 34.884276])

	#instance = MyStreamListener()
	# instance.on_status()
