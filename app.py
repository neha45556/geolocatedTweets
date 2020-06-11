# install Flask using "pip install flask-restful"
# run this app to get the server up
# access it by going to http://127.0.0.1:5000/ or whatever address the server says it is running on

from flask import Flask
from flask_restful import Api, Resource, reqparse
import json
from collections import Counter
import math

app = Flask(__name__)
api = Api(app)

# mock values, this will be filled with the index
with open('example.json') as f:
    index_values = json.load(f)


class index(Resource):

    
    # The get method is used to retrieve a particular index details by specifying the name:
    # /index/search?term=search_term&page=1&ranking=default returns the first page of 10 results after searching for "search_term" using the default ranking algorithm. 
    # more recent tweets should have higher score
    # ranking is based on vector space model using tf, probably do difference in minutes * .001
    def get(self, name):
        index_list = []
        for i in range(len(index_values)):
            tweet_text = list(index_values[i]["text"].lower().split(' '))
            search_term = list(name.lower().split(' '))

            # counts term frequencies
            count_tweet = Counter(tweet_text)
            count_term = Counter(search_term)

            # remove duplicates from text
            tweet_text = list(dict.fromkeys(tweet_text))
            search_term = list(dict.fromkeys(search_term))
            # loop through all the words of biggest list
            if(len(tweet_text) >= len(search_term)):
                max_list = tweet_text
                min_list = search_term
            else:
                max_list = search_term
                min_list = tweet_text

            # calculate numerator for vector space model
            numerator = 0
            for k in range(len(max_list)):
                word = max_list[k]
                numerator += count_tweet[word] * count_term[word]
            
            #calculate denominator for vector space model
            lhs = 0
            rhs = 0
            for j in range(len(tweet_text)):
                word = tweet_text[j]
                rhs += pow(count_tweet[word], 2)
            
            for x in range(len(search_term)):
                word = search_term[x]
                lhs += pow(count_term[word], 2)

            denominator = math.sqrt(rhs*lhs)

            relevance = 0
            if(denominator != 0):
                relevance = numerator / denominator

            index_values[i]["rank"] = relevance
            if(relevance > .1):
                index_list.append(index_values[i])




        if index_list:  
            # sort and return the top 10 based on ranking   
            top_ten = []

            
            # for it in range(len(index_values)):
            #     max = index_values[it]["rank"]
            top_ten = index_list[:10]
            return top_ten, 200

        return "search term not found", 404

      
api.add_resource(index, "/index/<string:name>")

app.run(debug=True)