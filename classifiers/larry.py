import random
import tweepy
from tweepy.error import TweepError

#Refactor
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

#Class that interfaces with Twitter, to pull out tweets and friends.
#We need `tweet_mode="extended"` so that we can get the fulltext of the tweet.
#Otherwise, the spaccy Twitter API will just cut off the tweets (or
#retweets or quotes).
class Larry:
  #Initialises Tweepy
  def __init__(self):
    self.auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
    self.auth.secure=True
    self.auth.set_access_token(access_token, access_token_secret)
    self.api=tweepy.API(self.auth)

  #Returns tweets by user's screenname
  def get_tweets_by_screenname(self, screen_name, count=200):
    chirps=self.api.user_timeline(screen_name=screen_name, count=count,
        tweet_mode="extended")
    return chirps

  #Returns tweets by user's id
  def get_tweets_by_userid(self, user_id, count=200):
    try:
      chirps=self.api.user_timeline(user_id=user_id, count=count,
        tweet_mode="extended")
      return chirps
    except TweepError as e:
      print("Caught error while getting tweets by user id: {0}".format(e))
      raise

  #Returns the users the parameterised user is following – in Twitter parlance,
  #this is "friends" instead of "following". I guess "following" is a verb, and
  #sounds odd as a noun?
  def get_friends_ids(self, screen_name, count=100):
    friends=self.api.friends_ids(screen_name)
    #Protecting against many many friends. Let's keep a limit on the number of
    #friends displayed, but shuffle this so that, well, we don't only get the
    #recently followed.
    random.shuffle(friends)
    if len(friends) >= count:
      return friends[0:count]
    else:
      return friends

  #Return the original tweet
  def get_tweet_by_id(self, tweet_id):
    original=self.api.get_status(tweet_id, tweet_mode="extended")
    return original

  def get_favourites_by_screenname(self, screen_name, count=200):
    favourites=self.api.favorites(screen_name=screen_name, count=count,
        tweet_mode="extended")
    return favourites

  def get_favourites_by_userid(self, userid, count=200):
    favourites=self.api.favorites(user_id=userid, count=count,
        tweet_mode="extended")
    return favourites

  def get_follower_count_for_user(self, screen_name):
    user = self.api.get_user(screen_name)
    if user:
      return user.followers_count
    else:
      return 0
