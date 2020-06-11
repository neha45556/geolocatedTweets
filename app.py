# install Flask using "pip install flask-restful"
# run this app to get the server up
# access it by going to http://127.0.0.1:5000/ or whatever address the server says it is running on

from flask import Flask
from flask_restful import Api, Resource, reqparse
import json

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
            tweet_text = set(index_values[i]["text"].split(' '))
            search_term = set(name.lower().split(' '))
          
            if(search_term == tweet_text):
                index_list.append(index_values[i])

        if index_list:  
            # sort and return the top 10 based on ranking   
            return index_list, 200

        return "search term not found", 404

      
api.add_resource(index, "/index/<string:name>")

app.run(debug=True)