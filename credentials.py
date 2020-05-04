#variables that contain the user credentials to access Twitter API

import tweepy
import json

#class TwitterStreamer():
#	def stream_tweets(self,fetched tweets_filename
class MyStreamListener(tweepy.StreamListener):
	#def _init_(self,api):
	#	self.api = api
	#	self.me = api.me()

	def on_status(self,tweet):
		#print(f"{tweet.user.name}:{tweet.text}")
		print(tweet.text)
		return True
	def on_error(self, status):
		print(status)

#authenticate to Twitter	
auth = tweepy.OAuthHandler("E0b6PlhPOGqJtqeKTRda74SLS","3iLsGyLf95lQPFbzWGDhjLtLuGBO5CG2TEMhniqwFrqsFJBXMe")
auth.set_access_token("3500144893-zpXqTRLyBAEmClgbC1RUDGX1ggyQ901a4OTHVUr","GaVhSEpGxctyIY4zBn11tSNJNMt72naUjB1BhNT51iV0V")

api = tweepy.API(auth, wait_on_rate_limit =True, wait_on_rate_limit_notify=True)
tweets_listener = MyStreamListener()
stream = tweepy.Stream(api.auth, tweets_listener)
stream.filter(coordinates = 34.052235,-118.243683)


