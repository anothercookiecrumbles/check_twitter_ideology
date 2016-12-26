import json
import os
import pickle
import sys
sys.path.append('../classifiers/')

from larry import Larry
from tweeper import get_tweets
from tweepy.error import TweepError

from flask import Flask, render_template, send_from_directory, redirect


app=Flask(__name__, static_url_path='')
app.secret_key = "secret key"

#Interface into Twitter using tweepy
birdy=Larry()

def load_file(file_to_load):
  current_directory=os.path.dirname(os.path.abspath(__file__))
  loadable=current_directory + "/" + file_to_load
  if os.path.isfile(loadable):
    with open(loadable, 'rb') as to_load:
      returnable = pickle.load(to_load)
    print("Loading {0}".format(file_to_load))
    return returnable

#Load vectorizer
cv = load_file("../classifiers/count_vectorizer.pkl")

#Load classifier
clf = load_file("../classifiers/classifier.pkl")

@app.route('/js/<path:path>')
def send_js(path):
  return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
  return send_from_directory('css', path)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/search/<twitter_handle>', methods=["POST"])
def profile_friends(twitter_handle):
  print("Finding friends for {0}".format(twitter_handle))
  try:
    friends=birdy.get_friends_ids(twitter_handle)
    print("Found {0} friends".format(len(friends)))
    ideology=list() #As JavaScript is effing terrible and doesn't have a dict.
    for friend in friends:
      #If we want _all_ the friends, we have to search by id, not screen_name.
      #Searching using screen_name only gets us the last 20 friends.
      tweets=get_tweets([friend], use_screen_name=False)
      keys=list(tweets.keys())
      #Concatenate all tweets into a single string so that we can run the
      #CountVectorizer against this.
      if keys:
        enlisted_tweets=[" ".join(tweets[keys[0]])]
        vector=cv.transform(enlisted_tweets)
        score=clf.predict(vector)
        followers=birdy.get_follower_count_for_user(keys[0])
        if (followers >= 0):
          ideology.append((keys[0], score[0], followers)) #So we just do a list of tuples.
    response = dict()
    response["handle"]=twitter_handle
    response["friends"]=ideology
    return json.dumps(response)
  except TweepError as e:
    print(e)
    return json.dumps({"Error": "Unable to get details for " +
      "{0}.".format(twitter_handle)})

