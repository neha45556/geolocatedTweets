# CS172: Twitter Search Engine: Part A And Part B

Prepared by: Daniel Ma (dma012@ucr.edu), Jeremy Taraba (jtara006@ucr.edu), Neha Gupta (ngupt009@ucr.edu)

## Part A: Build a Web Crawler for edu pages, or a geotagged Twitter post collector

## Collaboration Details PART A

* Daniel: JSON data formatting, URL crawling, concurrency issues.
* Neha: Twitter API setup and abstraction, creating files and output data, Memory Management
* Jeremy: Continuing Twitter API functionality, folder size and file size management, creating files



## Overview

The Twitter Engine is built on the Tweepy library for Python 3. It collects Tweets
from specified areas and stores them as JSON data.  The data includes the Tweet author,
text, and location Tweeted (if available).  Furthermore, the engine stores the URL and
page title of URLs in the Tweet body.  

The data is broken up into multiple JSON files of configurable size for easy parsing.

## Required packages

* Python 3.6+ (for f-strings)
* Python Tweepy 3.5+
* Python lxml
* Python requests 2.18+

## Architecture

The Engine consists of 2 threads: a streaming thread, and a serializing/parsing thread.
The streaming thread maintains a connection to Twitter's Streaming API, and inserts
data into a queue for parsing or saving. The serializing thread parses data from this
queue, and attempts to crawl any URLs found in the tweet body. The serializing thread
also occasionally writes the data to disk in a series of large JSON files.

## Data collection

The Engine maintains a connection to the Twitter Streaming API that queues data for
parsing and saving. Data is queued in a Python dictionary, which has a format that
resembles the output JSON format. During this stage, the data includes the name,
tweet body, and geolocation data (if available).

Parsing involves scanning the tweet for URLs and storing the title of these URLs
as data.  Parsing is done in a separate thread to prevent the Streaming thread
from blocking. On some machines or VMs, opening a connection can take a very
long time.

On these machines, parsing can fall behind data collection.  When this happens,
some data skips the parsing queue.  This data is saved, but has uncrawled
URLs in the body.

The data is mostly kept in memory, but is flushed asynchronously to disk at regular,
configurable intervals.  The data can be broken up into multiple files.  The breaks
can be configured, but are not very precise; file size can vary up to 20% from the desired
file size, depending on provided parameters.

## Limitations

Most Tweets do not come with exact location data, or any location data at all.  This is
because most Twitter users choose not to provide this data to Twitter.

On some systems or networks, fetching a URL can be extremely slow.  This can be a bottleneck
in the parsing process.  If parsing falls behind the Twitter stream, many tweets that contain
URLs will not contain metadata for those URLs.  This limitation can be circumvented by using
Twitter's built-in API for digesting Tweet URLs, rather than manually crawling these URLs on
the application side.

## Usage instructions

Start with `./crawler.sh`.  Configuration options can be adjusted in `config.json`. The
configuration options are generally self-explanatory, but must be written in valid JSON.

The last configuration option ("bounding boxes to track") is a list of pairs of longitude/latitude
coordinates. Each pair of coordinates specifies a bounding box from which to collect Tweets, with
the southwest coordinates specified first.

## Screenshots

### JSON output with testing config

![JSON output alongside command running and configuration options][cap1]

### JSON output with testing config 2

![JSON output alongside command running and configuration options][cap2]

### JSON output with testing config 3

![JSON output alongside command running and configuration options][cap3]

### File size variation with testing config

![JSON output alongside command running and configuration options][cap4]

### Program output with "production" config

![Non-testing config options][cap5]

[cap1]: https://github.com/neha45556/geolocatedTweets/raw/master/images/1.png
[cap2]: https://github.com/neha45556/geolocatedTweets/raw/master/images/2.png
[cap3]: https://github.com/neha45556/geolocatedTweets/raw/master/images/3.png
[cap4]: https://github.com/neha45556/geolocatedTweets/raw/master/images/4.png
[cap5]: https://github.com/neha45556/geolocatedTweets/raw/master/images/5.png



## Part B: Build index and Web-based search interface

## Collaboration Details PART B

* Daniel: Lucene insertion, server backend development
* Neha: Lucene processing, website development, document relevance analysis
* Jeremy: Lucene processing, server backend development, document relevance analysis

## Overview

The Twitter Engine is built on the Tweepy library for Python 3. It collects Tweets
from specified areas and stores them as JSON data.  The data includes the Tweet author,
text, and location Tweeted (if available).  Furthermore, the engine stores the URL and
page title of URLs in the Tweet body.  

The data is broken up into multiple JSON files of configurable size for easy parsing.

## Architecture
Used apache and Lucene as well as tested using a REST API server to rank and return the top ten results.

## Index Structures

Using Lucene we parsed the incoming tweets based on Username, Tweet text, Links, URL, and Title.

## Search Algorithm 
Vector space model with time relevance which decreases the score the more time that pass since the initial search.  We chose this ranking algorithm because it is fairly simple to implement and run on our system.


## Build Index Using Lucene

Using Lucene we create an app which parses the JSON objects of your big files form Part A and inserts them into Lucene. It handles  fields like username, text, followers, time, location, and so on.  We specifically used PyLucene in order to wrap Java Lucene and access its components from Python. 

## Create a Web-based interface

We created a web interface which has a simple text box that accepts query terms. These terms can be searched by pressing enter or clicking the search button which will then generate the top 10 indexes based on a vector space ranking model. 

## Limitation of the System

Some limitation are not taking into account the URL, links or location that was provided with the tweets from tweepy. We could have used these to either better rank the tweets or to geo locate the tweets. Also in the future we would like to add the functionality to only search tweets within a certain radius of the user’s location to provide more relevant information.


## Instructions on how to deploy the system
Run ./crawler.sh to procure the data from the tweets then compile the indexer with `./compile_indexer.sh` and run it with `./run_indexer.sh`. This will store the index files in the `index` folder. 
    
    
## A web-application (e.g. Web Archive) 
Using Apache we were able to launch a working application with server at http://cubesphere.net:9999/hello/search

## Screenshots
