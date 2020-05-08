#variables that contain the user credentials to access Twitter API

import tweepy
import json
import os,sys
import io	#gives backward compatibility with python 2
# from tweepy.streaming import StreamListener
# from tweepy import OAuthHandler
# from tweepy import Stream


#heads up: this takes a long time if your gonna do the full 2GB, it already takes a long time just for 5KB


#this is for one file size, we need separate files of 10MB all adding up to 2GB
#for testing it might be faster to make separate files of 1KB up to 5KB
MAX_FILE_SIZE = 5000		#Replace this with 2000000000 for 2GB bytes, can use 5000 for 5KB for testing
counter = 0
io.open('testfile.json', 'w+', encoding="utf-8").close() 	#empties the file and also creates the file if it doesnt exist

class MyStreamListener(tweepy.StreamListener):

	
	def _init_(self, e):
		self.max_file_size = 20
		self.cntr = 1
		#io.open('testfile.json', 'w+', encoding="utf-8").close() 	#empties the file and also creates the file if it doesnt exist

	# def create(self,tweet):
	# 	cntr = 0
	# 	max_file_size = 10000
	# 	json_file = io.open('testfile.json', 'w+', encoding="utf-8") 
	# 	while (cntr < 10):
	# 		if (os.stat('testfile.json').st_size < max_file_size):
	# 			json_file.write(tweet.text)
	# 			json_file.write('\n')
	# 			#self.create(tweet)
	# 		else:
	# 			cntr = cntr + 1
	# 	json_file.close()

	# def create(self,tweet):
	# 	max_file_size = 10
	# 	json_file = io.open('testfile.json', 'a', encoding="utf-8") 
	# 	while (os.stat('testfile.json').st_size < max_file_size):
	# 		json_file.write(tweet)
	# 		json_file.write('\n')
	# 	json_file.close()


		#this prints to screen
		#note: os.stat('testfile.json').st_size is in bytes 2GB = 2e+9 bytes

		#-------------make separate files not all in one file-----------------

	def on_status(self,tweet):
		if(os.stat('testfile.json').st_size >= MAX_FILE_SIZE):
			exit()
		#print("print st_size = " + str(os.stat('testfile.json').st_size))
		#print(tweet.text)		#uncomment this if you want to see the tweets being printed out
		json_file = io.open('testfile.json', 'a', encoding="utf-8") 
		json_file.write(tweet.text)
		json_file.write('\n')
		json_file.close()
		#print(f"{tweet.user.name}:{tweet.text}")1
		#self.create(tweet.text)
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
	#instance.on_status()
