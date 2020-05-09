# CS172: Twitter Search Engine: Part A
Prepared by: Daniel Ma (dma012@ucr.edu), Jeremy Taraba (jtara006@ucr.edu), Neha Gupta (ngupt009@ucr.edu)

## Collaboration Details
* Daniel: JSON schema, data serialization, URL crawling, concurrency.
* Neha: 
* Jeremy: 

## Overview
The Twitter Engine is built on the Tweepy library for Python 3. It collects Tweets
from specified areas and stores them as JSON data.  The data includes the Tweet author,
text, and location Tweeted (if available).  Furthermore, the engine stores the URL and
page title of URLs in the Tweet body.  

The data is broken up into multiple JSON files of configurable size for easy parsing.

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

## Data structures

